from fastapi import APIRouter, Depends
import traceback

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
            f"Monthly summary: Revenue RM {float(summary['total_inflow']):.2f}, "
            f"Expenses RM {float(summary['total_outflow']):.2f}, "
            f"Net RM {float(summary['net_cash_flow']):.2f}, "
            f"{summary['transaction_count']} transactions"
        )
    except Exception as e:
        print(f"Chat context (accounting) error: {e}")
        traceback.print_exc()

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
    except Exception as e:
        print(f"Chat context (score) error: {e}")
        traceback.print_exc()

    context = "\n".join(context_parts) if context_parts else ""

    # Strip current user message from history to avoid duplication
    # (invoke_claude appends user_message separately)
    history = req.conversation_history
    if history and history[-1].get("role") == "user":
        history = history[:-1]

    response = chat(req.message, history, context)
    return ChatResponse(response=response)
