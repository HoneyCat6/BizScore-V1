from fastapi import APIRouter, Depends

from routers.auth import get_current_owner_id
from services.chatbot import chat
from services.wallet_service import WalletService
from services.accounting_engine import AccountingEngine
from schemas.models import ChatMessage, ChatResponse
from dynamo import get_table, TABLE_SCORES

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/message", response_model=ChatResponse)
def send_message(req: ChatMessage, owner_id: str = Depends(get_current_owner_id)):
    # Build context from owner's data
    context_parts = []

    try:
        summary = AccountingEngine.get_summary(owner_id, "month")
        context_parts.append(
            f"Monthly summary: Revenue RM {summary['total_inflow']:.2f}, "
            f"Expenses RM {summary['total_outflow']:.2f}, "
            f"Net RM {summary['net_cash_flow']:.2f}, "
            f"{summary['transaction_count']} transactions"
        )
    except Exception:
        pass

    try:
        score_table = get_table(TABLE_SCORES)
        resp = score_table.query(
            KeyConditionExpression="owner_id = :oid",
            ExpressionAttributeValues={":oid": owner_id},
            ScanIndexForward=False,
            Limit=1,
        )
        items = resp.get("Items", [])
        if items:
            s = items[0]
            context_parts.append(
                f"Latest score: {int(s['total_score'])}/850 ({s.get('tier', '')})"
            )
    except Exception:
        pass

    context = "\n".join(context_parts) if context_parts else ""

    response = chat(req.message, req.conversation_history, context)
    return ChatResponse(response=response)
