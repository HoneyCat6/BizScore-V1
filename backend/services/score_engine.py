import math
from datetime import datetime, timezone, timedelta
from collections import defaultdict

from services.wallet_service import WalletService


def _get_all_transactions(owner_id: str) -> list[dict]:
    """Get all non-topup transactions for scoring."""
    txns = WalletService.get_transactions(owner_id, limit=200)
    return [t for t in txns if t.get("category") != "topup"]


def _score_clamp(value: float, max_pts: int) -> int:
    return max(0, min(max_pts, int(round(value))))


def _log_scale(value: float, midpoint: float, max_pts: int) -> int:
    if value <= 0:
        return 0
    scaled = max_pts * (math.log(1 + value) / math.log(1 + midpoint * 2))
    return _score_clamp(scaled, max_pts)


def calculate_score(owner_id: str) -> dict:
    txns = _get_all_transactions(owner_id)

    if not txns:
        return _empty_score()

    # Separate inflows and outflows
    inflows = [t for t in txns if t["direction"] == "inflow"]
    outflows = [t for t in txns if t["direction"] == "outflow"]

    total_revenue = sum(t["amount"] for t in inflows)
    total_expenses = sum(t["amount"] for t in outflows)

    # Group by date for time-series analysis
    daily_revenue = defaultdict(float)
    daily_txn_count = defaultdict(int)
    monthly_revenue = defaultdict(float)
    counterparties = defaultdict(lambda: {"total": 0.0, "months": set()})

    for t in inflows:
        date_str = t.get("txn_date", "")[:10]
        month_str = date_str[:7]
        daily_revenue[date_str] += t["amount"]
        daily_txn_count[date_str] += 1
        monthly_revenue[month_str] += t["amount"]

        cp = t.get("counterparty_phone") or t.get("counterparty_name", "")
        if cp:
            counterparties[cp]["total"] += t["amount"]
            counterparties[cp]["months"].add(month_str)

    # Group outflows by category
    expense_by_cat = defaultdict(float)
    for t in outflows:
        expense_by_cat[t.get("category", "other_expense")] += t["amount"]

    # Parse date range
    dates = sorted(daily_revenue.keys())
    if dates:
        first_date = datetime.fromisoformat(dates[0])
        account_age_days = (datetime.now(timezone.utc) - first_date.replace(tzinfo=timezone.utc)).days
    else:
        account_age_days = 0

    # ====== COMPONENT 1: Revenue & Cash Flow (0-250) ======
    c1_details = {}

    # Total revenue (log scale, midpoint ~5000) — 0-80
    rev_score = _log_scale(total_revenue, 5000, 80)
    c1_details["revenue_total"] = round(total_revenue, 2)

    # Profit margin — 0-70
    margin = (total_revenue - total_expenses) / total_revenue if total_revenue > 0 else 0
    margin_score = _score_clamp(margin * 100, 70) if margin > 0 else 0
    c1_details["profit_margin"] = round(margin * 100, 1)

    # Revenue consistency (lower std dev = better) — 0-40
    if len(daily_revenue) > 1:
        avg_daily = total_revenue / max(len(daily_revenue), 1)
        variance = sum((v - avg_daily) ** 2 for v in daily_revenue.values()) / len(daily_revenue)
        cv = (variance ** 0.5) / avg_daily if avg_daily > 0 else 1
        consistency_score = _score_clamp((1 - min(cv, 1)) * 40, 40)
    else:
        consistency_score = 0
    c1_details["consistency_cv"] = round(cv if len(daily_revenue) > 1 else 0, 2)

    # Cash flow positivity — 0-30
    months_positive = sum(1 for m, r in monthly_revenue.items() if r > sum(
        t["amount"] for t in outflows if t.get("txn_date", "")[:7] == m
    ))
    total_months = max(len(monthly_revenue), 1)
    cashflow_score = _score_clamp((months_positive / total_months) * 30, 30)

    # Revenue per transaction — 0-30
    avg_sale = total_revenue / max(len(inflows), 1)
    rpt_score = _log_scale(avg_sale, 50, 30)
    c1_details["avg_sale_size"] = round(avg_sale, 2)

    c1_total = rev_score + margin_score + consistency_score + cashflow_score + rpt_score
    c1_total = min(c1_total, 250)

    # ====== COMPONENT 2: Growth & Momentum (0-200) ======
    c2_details = {}

    sorted_months = sorted(monthly_revenue.keys())
    if len(sorted_months) >= 2:
        recent = sorted_months[-min(3, len(sorted_months)):]
        older = sorted_months[:max(1, len(sorted_months) - 3)]
        recent_avg = sum(monthly_revenue[m] for m in recent) / len(recent)
        older_avg = sum(monthly_revenue[m] for m in older) / len(older) if older else recent_avg
        growth_rate = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
        growth_score = _score_clamp((min(growth_rate, 1) + 0.2) * 70, 70)
    else:
        growth_rate = 0
        growth_score = 10
    c2_details["growth_rate"] = round(growth_rate * 100, 1)

    # Transaction volume growth — 0-50
    monthly_txn_counts = defaultdict(int)
    for t in txns:
        m = t.get("txn_date", "")[:7]
        monthly_txn_counts[m] += 1
    if len(sorted_months) >= 2:
        recent_txns = sum(monthly_txn_counts.get(m, 0) for m in recent)
        older_txns = sum(monthly_txn_counts.get(m, 0) for m in older)
        vol_growth = (recent_txns - older_txns) / max(older_txns, 1)
        vol_score = _score_clamp((min(vol_growth, 1) + 0.2) * 50, 50)
    else:
        vol_score = 10

    # New customer acquisition — 0-40
    unique_customers = len(counterparties)
    cust_acq_score = _log_scale(unique_customers, 50, 40)
    c2_details["unique_customers"] = unique_customers

    # Avg txn size growth — 0-20
    txn_size_score = 10  # Default mid-range for hackathon

    # Reinvestment ratio — 0-20
    capex = expense_by_cat.get("capital_expenditure", 0) + expense_by_cat.get("asset_purchase", 0)
    reinvest_ratio = capex / total_revenue if total_revenue > 0 else 0
    reinvest_score = _score_clamp(min(reinvest_ratio, 0.3) / 0.3 * 20, 20)
    c2_details["reinvestment_ratio"] = round(reinvest_ratio * 100, 1)

    c2_total = growth_score + vol_score + cust_acq_score + txn_size_score + reinvest_score
    c2_total = min(c2_total, 200)

    # ====== COMPONENT 3: Customer & Market Strength (0-175) ======
    c3_details = {}

    # Unique counterparties — 0-60
    diversity_score = _log_scale(unique_customers, 100, 60)
    c3_details["customer_count"] = unique_customers

    # Repeat customer rate — 0-50
    repeat_customers = sum(1 for cp in counterparties.values() if len(cp["months"]) >= 2)
    repeat_rate = repeat_customers / max(unique_customers, 1)
    repeat_score = _score_clamp(repeat_rate * 50, 50)
    c3_details["repeat_rate"] = round(repeat_rate * 100, 1)

    # Transaction frequency — 0-35
    active_days = len(daily_txn_count)
    total_days = max(account_age_days, 1)
    freq_ratio = active_days / total_days
    freq_score = _score_clamp(freq_ratio * 35, 35)
    c3_details["active_days_pct"] = round(freq_ratio * 100, 1)

    # Customer concentration — 0-30
    if counterparties and total_revenue > 0:
        top3_revenue = sum(
            sorted([cp["total"] for cp in counterparties.values()], reverse=True)[:3]
        )
        concentration = top3_revenue / total_revenue
        conc_score = _score_clamp((1 - concentration) * 30, 30)
    else:
        conc_score = 0
        concentration = 0
    c3_details["top3_concentration"] = round(concentration * 100, 1)

    c3_total = diversity_score + repeat_score + freq_score + conc_score
    c3_total = min(c3_total, 175)

    # ====== COMPONENT 4: Operational Stability (0-125) ======
    c4_details = {}

    # Account age — 0-35
    age_score = _score_clamp(min(account_age_days, 365) / 365 * 35, 35)
    c4_details["account_age_days"] = account_age_days

    # Recording consistency — 0-30
    rec_score = _score_clamp(freq_ratio * 30, 30)

    # Regular expense payments — 0-25
    regular_cats = {"rent", "utilities", "salary"}
    regular_count = sum(1 for c in regular_cats if c in expense_by_cat)
    reg_score = _score_clamp((regular_count / 3) * 25, 25)

    # Operating days per week — 0-20
    if dates and len(dates) >= 7:
        weekdays = set()
        for d in dates[-28:]:
            try:
                weekdays.add(datetime.fromisoformat(d).weekday())
            except ValueError:
                pass
        op_days_score = _score_clamp((len(weekdays) / 7) * 20, 20)
    else:
        op_days_score = 5

    # Categorization quality — 0-15
    categorized = sum(1 for t in outflows if t.get("category") != "other_expense")
    cat_quality = categorized / max(len(outflows), 1)
    cat_score = _score_clamp(cat_quality * 15, 15)
    c4_details["categorization_quality"] = round(cat_quality * 100, 1)

    c4_total = age_score + rec_score + reg_score + op_days_score + cat_score
    c4_total = min(c4_total, 125)

    # ====== COMPONENT 5: Financial Management (0-100) ======
    c5_details = {}

    # Expense ratio — 0-30
    opex = total_expenses - expense_by_cat.get("cost_of_goods", 0) - capex
    exp_ratio = opex / total_revenue if total_revenue > 0 else 1
    exp_score = _score_clamp((1 - min(exp_ratio, 1)) * 30, 30)
    c5_details["expense_ratio"] = round(exp_ratio * 100, 1)

    # COGS ratio — 0-25
    cogs = expense_by_cat.get("cost_of_goods", 0)
    cogs_ratio = cogs / total_revenue if total_revenue > 0 else 0
    # Sweet spot: 20-60% COGS is healthy
    if 0.2 <= cogs_ratio <= 0.6:
        cogs_score = 25
    elif cogs_ratio < 0.2:
        cogs_score = _score_clamp(cogs_ratio / 0.2 * 25, 25)
    else:
        cogs_score = _score_clamp((1 - (cogs_ratio - 0.6) / 0.4) * 25, 25)
    c5_details["cogs_ratio"] = round(cogs_ratio * 100, 1)

    # Diversified expenses — 0-20
    expense_cats_used = len([c for c in expense_by_cat if c != "topup"])
    div_score = _score_clamp(min(expense_cats_used, 5) / 5 * 20, 20)

    # Payment regularity — 0-15
    reg_pay_score = reg_score * 15 // 25  # Reuse from operational stability

    # No large unexplained outflows — 0-10
    if outflows:
        avg_out = total_expenses / len(outflows)
        large_unexplained = sum(
            1 for t in outflows
            if t["amount"] > avg_out * 5 and t.get("category") == "other_expense"
        )
        unexplained_score = _score_clamp((1 - large_unexplained / max(len(outflows), 1)) * 10, 10)
    else:
        unexplained_score = 5

    c5_total = exp_score + cogs_score + div_score + reg_pay_score + unexplained_score
    c5_total = min(c5_total, 100)

    # ====== TOTAL ======
    total = c1_total + c2_total + c3_total + c4_total + c5_total
    total = min(total, 850)

    tier = _get_tier(total)

    return {
        "total_score": total,
        "tier": tier,
        "components": [
            {"name": "Revenue & Cash Flow", "score": c1_total, "max_score": 250, "details": c1_details},
            {"name": "Growth & Momentum", "score": c2_total, "max_score": 200, "details": c2_details},
            {"name": "Customer & Market Strength", "score": c3_total, "max_score": 175, "details": c3_details},
            {"name": "Operational Stability", "score": c4_total, "max_score": 125, "details": c4_details},
            {"name": "Financial Management", "score": c5_total, "max_score": 100, "details": c5_details},
        ],
        "data_snapshot": {
            "total_revenue": round(total_revenue, 2),
            "total_expenses": round(total_expenses, 2),
            "net_profit": round(total_revenue - total_expenses, 2),
            "transaction_count": len(txns),
            "unique_customers": unique_customers,
            "account_age_days": account_age_days,
            "profit_margin_pct": round(margin * 100, 1) if total_revenue > 0 else 0,
            "growth_rate_pct": round(growth_rate * 100, 1),
        },
    }


def _get_tier(score: int) -> str:
    if score >= 700:
        return "Thriving"
    elif score >= 550:
        return "Healthy"
    elif score >= 400:
        return "Emerging"
    elif score >= 250:
        return "Early-Stage"
    else:
        return "Pre-Launch"


def _empty_score() -> dict:
    return {
        "total_score": 0,
        "tier": "Pre-Launch",
        "components": [
            {"name": "Revenue & Cash Flow", "score": 0, "max_score": 250, "details": {}},
            {"name": "Growth & Momentum", "score": 0, "max_score": 200, "details": {}},
            {"name": "Customer & Market Strength", "score": 0, "max_score": 175, "details": {}},
            {"name": "Operational Stability", "score": 0, "max_score": 125, "details": {}},
            {"name": "Financial Management", "score": 0, "max_score": 100, "details": {}},
        ],
        "data_snapshot": {},
    }
