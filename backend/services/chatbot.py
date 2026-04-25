import traceback

from services.bedrock_client import invoke_claude


CHATBOT_SYSTEM = """You are BizScore Assistant, a friendly helper for small business owners.
You help them understand their business performance, wallet transactions, and BizScore.

Key rules:
- Use SIMPLE language (many users have limited financial literacy)
- Keep answers SHORT (2-3 sentences max unless they ask for detail)
- Be warm, encouraging, and supportive
- Reference their actual business data when available
- Help them understand how to improve their BizScore
- If asked about loans, explain they can generate a Business Performance Report to show any loan agency
- You can explain what each score component means

You know about:
- BizScore measures business health (0-850) across 5 areas: Revenue & Cash Flow, Growth & Momentum, Customer Strength, Operational Stability, Financial Management
- All incoming wallet payments are auto-counted as sales
- Outgoing payments should be categorized (cost of goods, rent, salary, etc.)
- Better categorization = better score
- Consistent daily usage improves the Operational Stability score
- More unique customers = better Customer & Market score"""


def chat(message: str, conversation_history: list[dict], context: str = "") -> str:
    """Process a chat message with optional business context."""
    enriched_system = CHATBOT_SYSTEM
    if context:
        enriched_system += f"\n\nUser's current business context:\n{context}"

    try:
        return invoke_claude(
            enriched_system,
            message,
            max_tokens=300,
            conversation_history=conversation_history,
        )
    except Exception as e:
        print(f"Chat error: {e}")
        traceback.print_exc()
        return (
            "I'm having trouble connecting right now. "
            "In the meantime, here are some tips: "
            "1) Record all your sales through the wallet daily, "
            "2) Categorize your expenses when you make payments, "
            "3) Check your Reports page to see your business health!"
        )
