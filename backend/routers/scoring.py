from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from routers.auth import get_current_owner_id
from services.score_engine import calculate_score
from services.explanation_gen import generate_explanation
from services.wallet_service import WalletService
from schemas.models import ScoreResult, ScoreComponent
from dynamo import get_table, TABLE_SCORES, TABLE_OWNERS

router = APIRouter(prefix="/api/score", tags=["score"])


def _convert_floats_to_decimal(obj):
    """Recursively convert all float values in a nested dict/list to Decimal."""
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: _convert_floats_to_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_floats_to_decimal(item) for item in obj]
    return obj


def _get_owner_info(owner_id: str) -> dict:
    table = get_table(TABLE_OWNERS)
    resp = table.query(
        IndexName="owner_id-index",
        KeyConditionExpression="owner_id = :oid",
        ExpressionAttributeValues={":oid": owner_id},
    )
    items = resp.get("Items", [])
    return items[0] if items else {}


@router.post("/calculate", response_model=ScoreResult)
def calculate(owner_id: str = Depends(get_current_owner_id)):
    # Calculate score from transaction data
    score_data = calculate_score(owner_id)

    # Get owner info for explanation
    owner_info = _get_owner_info(owner_id)

    # Generate AI explanation
    explanation = generate_explanation(score_data, owner_info)

    # Save to DynamoDB
    score_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()

    table = get_table(TABLE_SCORES)
    table.put_item(
        Item=_convert_floats_to_decimal({
            "owner_id": owner_id,
            "generated_at": now,
            "score_id": score_id,
            "total_score": score_data["total_score"],
            "tier": score_data["tier"],
            "components": score_data["components"],
            "explanation": explanation,
            "data_snapshot": score_data.get("data_snapshot", {}),
        })
    )

    return ScoreResult(
        score_id=score_id,
        owner_id=owner_id,
        total_score=score_data["total_score"],
        tier=score_data["tier"],
        components=[ScoreComponent(**c) for c in score_data["components"]],
        explanation=explanation,
        generated_at=now,
    )


@router.get("/latest", response_model=ScoreResult)
def get_latest(owner_id: str = Depends(get_current_owner_id)):
    table = get_table(TABLE_SCORES)
    resp = table.query(
        KeyConditionExpression="owner_id = :oid",
        ExpressionAttributeValues={":oid": owner_id},
        ScanIndexForward=False,
        Limit=1,
    )
    items = resp.get("Items", [])
    if not items:
        raise HTTPException(status_code=404, detail="No score found. Calculate one first.")

    item = items[0]
    return ScoreResult(
        score_id=item["score_id"],
        owner_id=item["owner_id"],
        total_score=int(item["total_score"]),
        tier=item.get("tier", ""),
        components=[ScoreComponent(**c) for c in item["components"]],
        explanation=item.get("explanation", ""),
        generated_at=item["generated_at"],
    )


@router.get("/history")
def get_history(owner_id: str = Depends(get_current_owner_id)):
    table = get_table(TABLE_SCORES)
    resp = table.query(
        KeyConditionExpression="owner_id = :oid",
        ExpressionAttributeValues={":oid": owner_id},
        ScanIndexForward=False,
        Limit=20,
    )
    items = resp.get("Items", [])
    return {
        "scores": [
            {
                "score_id": i["score_id"],
                "total_score": int(i["total_score"]),
                "tier": i.get("tier", ""),
                "generated_at": i["generated_at"],
            }
            for i in items
        ]
    }
