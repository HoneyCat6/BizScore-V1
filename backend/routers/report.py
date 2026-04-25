from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from routers.auth import get_current_owner_id
from services.report_generator import generate_pdf_report
from services.explanation_gen import generate_report_narrative
from services.accounting_engine import AccountingEngine
from dynamo import get_table, TABLE_SCORES, TABLE_OWNERS

router = APIRouter(prefix="/api/report", tags=["report"])


def _get_owner_info(owner_id: str) -> dict:
    table = get_table(TABLE_OWNERS)
    resp = table.query(
        IndexName="owner_id-index",
        KeyConditionExpression="owner_id = :oid",
        ExpressionAttributeValues={":oid": owner_id},
    )
    items = resp.get("Items", [])
    return items[0] if items else {}


@router.post("/generate")
def generate_report(owner_id: str = Depends(get_current_owner_id)):
    """Generate a PDF Business Performance Report from the latest score."""
    # Get latest score
    score_table = get_table(TABLE_SCORES)
    resp = score_table.query(
        KeyConditionExpression="owner_id = :oid",
        ExpressionAttributeValues={":oid": owner_id},
        ScanIndexForward=False,
        Limit=1,
    )
    items = resp.get("Items", [])
    if not items:
        raise HTTPException(status_code=404, detail="No score found. Calculate a score first.")

    score_item = items[0]
    owner_info = _get_owner_info(owner_id)
    pnl = AccountingEngine.get_pnl(owner_id, "month")

    # Build score_data from stored item
    score_data = {
        "total_score": int(score_item["total_score"]),
        "tier": score_item.get("tier", ""),
        "components": score_item.get("components", []),
        "data_snapshot": score_item.get("data_snapshot", {}),
    }

    # Generate AI narrative for the report
    narrative = generate_report_narrative(score_data, owner_info, pnl)

    # Generate PDF
    pdf_buf = generate_pdf_report(owner_info, score_data, pnl, narrative)

    business_name = owner_info.get("business_name", "business").replace(" ", "_")
    filename = f"BizScore_Report_{business_name}.pdf"

    return StreamingResponse(
        pdf_buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{score_id}/share")
def get_shared_report(score_id: str):
    """Public endpoint — no auth required. Returns score data for shared reports."""
    # Scan for the score by score_id (not ideal for production but fine for hackathon)
    score_table = get_table(TABLE_SCORES)
    resp = score_table.scan(
        FilterExpression="score_id = :sid",
        ExpressionAttributeValues={":sid": score_id},
        Limit=1,
    )
    items = resp.get("Items", [])
    if not items:
        raise HTTPException(status_code=404, detail="Report not found")

    score_item = items[0]
    owner_info = _get_owner_info(score_item["owner_id"])

    return {
        "business_name": owner_info.get("business_name", "N/A"),
        "business_type": owner_info.get("business_type", "N/A"),
        "owner_name": owner_info.get("name", "N/A"),
        "location": owner_info.get("location", ""),
        "total_score": int(score_item["total_score"]),
        "tier": score_item.get("tier", ""),
        "components": score_item.get("components", []),
        "explanation": score_item.get("explanation", ""),
        "generated_at": score_item.get("generated_at", ""),
        "data_snapshot": score_item.get("data_snapshot", {}),
    }
