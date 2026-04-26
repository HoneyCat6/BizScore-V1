from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from decimal import Decimal

from routers.auth import get_current_owner_id
from services.report_generator import generate_pdf_report
from services.explanation_gen import generate_report_narrative
from services.accounting_engine import AccountingEngine
from dynamo import get_table, TABLE_SCORES, TABLE_OWNERS

router = APIRouter(prefix="/api/report", tags=["report"])


def _convert_decimals_to_native(obj):
    """Recursively convert Decimal values to int or float in nested dicts/lists."""
    if isinstance(obj, Decimal):
        if obj == obj.to_integral_value():
            return int(obj)
        return float(obj)
    if isinstance(obj, dict):
        return {k: _convert_decimals_to_native(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_decimals_to_native(item) for item in obj]
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


@router.post("/generate")
def generate_report(owner_id: str = Depends(get_current_owner_id)):
    """Generate a PDF Business Performance Report from the latest score."""
    try:
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
        pnl = AccountingEngine.get_pnl(owner_id, 30)

        # Build score_data from stored item, converting DynamoDB Decimals to native types
        score_data = {
            "total_score": int(score_item["total_score"]),
            "tier": score_item.get("tier", ""),
            "components": _convert_decimals_to_native(score_item.get("components", [])),
            "data_snapshot": _convert_decimals_to_native(score_item.get("data_snapshot", {})),
        }
        pnl = _convert_decimals_to_native(pnl)

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
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"PDF generation error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


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
