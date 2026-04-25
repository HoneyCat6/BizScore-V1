from fastapi import APIRouter, Depends, Query

from routers.auth import get_current_owner_id
from services.accounting_engine import AccountingEngine
from schemas.models import AccountingSummary, PnLReport, CashFlowReport, CategoryBreakdown

router = APIRouter(prefix="/api/accounting", tags=["accounting"])


@router.get("/summary", response_model=AccountingSummary)
def get_summary(
    period: str = Query("month", regex="^(today|week|month|year)$"),
    owner_id: str = Depends(get_current_owner_id),
):
    return AccountingEngine.get_summary(owner_id, period)


@router.get("/pnl", response_model=PnLReport)
def get_pnl(
    period: str = Query("month", regex="^(month|quarter|year)$"),
    owner_id: str = Depends(get_current_owner_id),
):
    return AccountingEngine.get_pnl(owner_id, period)


@router.get("/cashflow", response_model=CashFlowReport)
def get_cashflow(
    period: str = Query("month", regex="^(month|quarter)$"),
    owner_id: str = Depends(get_current_owner_id),
):
    return AccountingEngine.get_cashflow(owner_id, period)


@router.get("/categories", response_model=list[CategoryBreakdown])
def get_categories(
    period: str = Query("month"),
    owner_id: str = Depends(get_current_owner_id),
):
    return AccountingEngine.get_categories(owner_id, period)
