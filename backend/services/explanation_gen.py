import json
from services.bedrock_client import invoke_claude


SCORE_EXPLANATION_SYSTEM = """You are BizScore AI, a business performance advisor for small business owners in emerging markets. 
Many of your users have limited financial literacy. You must:
- Use simple, clear language (no jargon)
- Be encouraging and constructive 
- Reference specific numbers from their data
- Give concrete, actionable improvement tips
- Keep it concise (3 short paragraphs max)

Format your response in 3 sections:
1. **Your Business Score** - What the score means in plain language
2. **Your Strengths** - What's going well (2-3 bullet points)  
3. **How to Improve** - Specific actions to boost the score (2-3 bullet points)"""


def generate_explanation(score_data: dict, owner_info: dict) -> str:
    """Generate a plain-language explanation of the business performance score."""
    user_message = f"""Generate a business performance explanation for this owner:

Business: {owner_info.get('business_name', 'Unknown')} ({owner_info.get('business_type', 'Unknown')})
Owner: {owner_info.get('name', 'Unknown')}

Score: {score_data['total_score']}/850 (Tier: {score_data['tier']})

Components:
{json.dumps(score_data['components'], indent=2, default=str)}

Financial Snapshot:
{json.dumps(score_data.get('data_snapshot', {}), indent=2, default=str)}"""

    try:
        return invoke_claude(SCORE_EXPLANATION_SYSTEM, user_message, max_tokens=800)
    except Exception as e:
        # Fallback if Bedrock is unavailable
        return _fallback_explanation(score_data)


REPORT_NARRATIVE_SYSTEM = """You are a professional business analyst writing a Business Performance Report for a microfinance loan agency.
The report should be:
- Professional but accessible
- Data-driven (cite specific numbers)
- Balanced (mention both strengths and areas for development)
- Structured with clear sections

Write a 4-section narrative:
1. **Executive Summary** - One paragraph overview of the business
2. **Financial Performance** - Revenue, profitability, cash flow analysis
3. **Business Strengths** - What makes this business a good candidate
4. **Areas for Development** - What the business should work on (framed constructively)"""


def generate_report_narrative(score_data: dict, owner_info: dict, pnl: dict) -> str:
    """Generate a formal report narrative suitable for loan agencies."""
    user_message = f"""Write a Business Performance Report narrative for:

Business: {owner_info.get('business_name', 'Unknown')} ({owner_info.get('business_type', 'Unknown')})
Owner: {owner_info.get('name', 'Unknown')}
Location: {owner_info.get('location', 'Not specified')}

Business Performance Score: {score_data['total_score']}/850 (Tier: {score_data['tier']})

Score Components:
{json.dumps(score_data['components'], indent=2, default=str)}

Profit & Loss Summary:
{json.dumps(pnl, indent=2, default=str)}

Financial Snapshot:
{json.dumps(score_data.get('data_snapshot', {}), indent=2, default=str)}"""

    try:
        return invoke_claude(REPORT_NARRATIVE_SYSTEM, user_message, max_tokens=1200)
    except Exception as e:
        return _fallback_report(score_data, pnl)


def _fallback_explanation(score_data: dict) -> str:
    s = score_data["total_score"]
    tier = score_data["tier"]
    snap = score_data.get("data_snapshot", {})

    return (
        f"**Your Business Score**\n"
        f"Your business scored {s} out of 850, placing you in the '{tier}' tier. "
        f"This score is based on your actual payment activity through the wallet.\n\n"
        f"**Your Strengths**\n"
        f"- Total revenue recorded: RM {snap.get('total_revenue', 0):,.2f}\n"
        f"- {snap.get('unique_customers', 0)} unique customers served\n"
        f"- {snap.get('transaction_count', 0)} transactions recorded\n\n"
        f"**How to Improve**\n"
        f"- Use your wallet consistently every day to build a stronger track record\n"
        f"- Categorize your expenses properly when making payments\n"
        f"- Grow your customer base by serving more unique customers"
    )


def _fallback_report(score_data: dict, pnl: dict) -> str:
    s = score_data["total_score"]
    tier = score_data["tier"]
    return (
        f"**Executive Summary**\n"
        f"This business has a BizScore of {s}/850 ({tier} tier). "
        f"Revenue: RM {pnl.get('revenue', 0):,.2f}, "
        f"Net Profit: RM {pnl.get('net_profit', 0):,.2f}.\n\n"
        f"**Financial Performance**\n"
        f"The business shows {'positive' if pnl.get('net_profit', 0) > 0 else 'negative'} profitability "
        f"with a gross profit of RM {pnl.get('gross_profit', 0):,.2f}.\n\n"
        f"**Business Strengths**\n"
        f"Active wallet usage demonstrates business engagement.\n\n"
        f"**Areas for Development**\n"
        f"Continue building transaction history for a more comprehensive assessment."
    )
