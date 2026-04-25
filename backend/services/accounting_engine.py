from datetime import datetime, timezone, timedelta
from collections import defaultdict

from services.wallet_service import WalletService

EXPENSE_CATEGORIES = {
    "cost_of_goods", "operating_expense", "salary", "rent",
    "utilities", "capital_expenditure", "asset_purchase",
    "loan_repayment", "other_expense",
}

CAPITAL_CATEGORIES = {"capital_expenditure", "asset_purchase"}


class AccountingEngine:
    @staticmethod
    def get_summary(owner_id: str, period: str = "month") -> dict:
        now = datetime.now(timezone.utc)
        if period == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        elif period == "week":
            start = (now - timedelta(days=7)).isoformat()
        elif period == "month":
            start = (now - timedelta(days=30)).isoformat()
        elif period == "year":
            start = (now - timedelta(days=365)).isoformat()
        else:
            start = (now - timedelta(days=30)).isoformat()

        end = now.isoformat()
        txns = WalletService.get_transactions(
            owner_id, start_date=start, end_date=end, limit=200
        )

        # Filter out topup transactions from accounting
        txns = [t for t in txns if t.get("category") != "topup"]

        total_in = sum(t["amount"] for t in txns if t["direction"] == "inflow")
        total_out = sum(t["amount"] for t in txns if t["direction"] == "outflow")

        return {
            "period": period,
            "total_inflow": round(total_in, 2),
            "total_outflow": round(total_out, 2),
            "net_cash_flow": round(total_in - total_out, 2),
            "transaction_count": len(txns),
        }

    @staticmethod
    def get_pnl(owner_id: str, days: int = 30) -> dict:
        now = datetime.now(timezone.utc)
        start = (now - timedelta(days=days)).isoformat()
        end = now.isoformat()
        txns = WalletService.get_transactions(
            owner_id, start_date=start, end_date=end, limit=500
        )
        txns = [t for t in txns if t.get("category") != "topup"]

        revenue = sum(t["amount"] for t in txns if t["direction"] == "inflow")
        cogs = sum(
            t["amount"] for t in txns
            if t["direction"] == "outflow" and t.get("category") == "cost_of_goods"
        )
        gross_profit = revenue - cogs

        expense_breakdown = defaultdict(float)
        total_opex = 0.0
        for t in txns:
            if t["direction"] == "outflow" and t.get("category") in EXPENSE_CATEGORIES:
                cat = t["category"]
                expense_breakdown[cat] += t["amount"]
                if cat not in CAPITAL_CATEGORIES and cat != "cost_of_goods":
                    total_opex += t["amount"]

        net_profit = gross_profit - total_opex

        return {
            "period": f"{days}d",
            "revenue": round(revenue, 2),
            "cost_of_goods": round(cogs, 2),
            "gross_profit": round(gross_profit, 2),
            "operating_expenses": round(total_opex, 2),
            "net_profit": round(net_profit, 2),
            "expense_breakdown": {k: round(v, 2) for k, v in expense_breakdown.items()},
        }

    @staticmethod
    def get_cashflow(owner_id: str, days: int = 30) -> dict:
        now = datetime.now(timezone.utc)
        start = (now - timedelta(days=days)).isoformat()
        end = now.isoformat()
        txns = WalletService.get_transactions(
            owner_id, start_date=start, end_date=end, limit=500
        )
        txns = [t for t in txns if t.get("category") != "topup"]

        op_in = sum(t["amount"] for t in txns if t["direction"] == "inflow")
        op_out = sum(
            t["amount"] for t in txns
            if t["direction"] == "outflow" and t.get("category") not in CAPITAL_CATEGORIES
        )
        cap_out = sum(
            t["amount"] for t in txns
            if t["direction"] == "outflow" and t.get("category") in CAPITAL_CATEGORIES
        )

        return {
            "period": f"{days}d",
            "operating_inflow": round(op_in, 2),
            "operating_outflow": round(op_out, 2),
            "capital_outflow": round(cap_out, 2),
            "net_cash_flow": round(op_in - op_out - cap_out, 2),
        }

    @staticmethod
    def get_categories(owner_id: str, days: int = 30) -> list[dict]:
        now = datetime.now(timezone.utc)
        start = (now - timedelta(days=days)).isoformat()
        end = now.isoformat()

        txns = WalletService.get_transactions(
            owner_id, start_date=start, end_date=end, limit=500
        )
        txns = [t for t in txns if t.get("category") != "topup"]

        cat_totals = defaultdict(lambda: {"total": 0.0, "count": 0})
        grand_total = 0.0

        for t in txns:
            cat = t.get("category", "unknown")
            cat_totals[cat]["total"] += t["amount"]
            cat_totals[cat]["count"] += 1
            grand_total += t["amount"]

        result = []
        for cat, data in sorted(cat_totals.items(), key=lambda x: -x[1]["total"]):
            result.append({
                "category": cat,
                "total": round(data["total"], 2),
                "count": data["count"],
                "percentage": round(data["total"] / grand_total * 100, 2) if grand_total > 0 else 0,
            })

        return result
