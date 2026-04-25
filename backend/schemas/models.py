from pydantic import BaseModel, Field
from enum import Enum


class OutflowCategory(str, Enum):
    cost_of_goods = "cost_of_goods"
    operating_expense = "operating_expense"
    salary = "salary"
    rent = "rent"
    utilities = "utilities"
    capital_expenditure = "capital_expenditure"
    asset_purchase = "asset_purchase"
    loan_repayment = "loan_repayment"
    other_expense = "other_expense"


INFLOW_CATEGORY = "sales_revenue"


# --- Auth ---
class RegisterRequest(BaseModel):
    phone: str = Field(..., min_length=8, max_length=20)
    pin: str = Field(..., min_length=4, max_length=6)
    name: str = Field(..., min_length=1, max_length=100)
    business_name: str = Field(..., min_length=1, max_length=200)
    business_type: str = Field(..., min_length=1, max_length=100)
    location: str = Field("", max_length=200)


class LoginRequest(BaseModel):
    phone: str
    pin: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    owner_id: str
    name: str
    business_name: str


class OwnerProfile(BaseModel):
    owner_id: str
    phone: str
    name: str
    business_name: str
    business_type: str
    location: str
    wallet_balance: float
    created_at: str


# --- Wallet ---
class TopUpRequest(BaseModel):
    amount: float = Field(..., gt=0)


class SendPaymentRequest(BaseModel):
    amount: float = Field(..., gt=0)
    recipient_phone: str = Field(..., min_length=8, max_length=20)
    category: OutflowCategory
    description: str = ""


class ReceivePaymentRequest(BaseModel):
    amount: float = Field(..., gt=0)
    payer_phone: str = Field("", max_length=20)
    payer_name: str = Field("", max_length=100)
    description: str = ""


class WalletBalance(BaseModel):
    balance: float
    currency: str = "MYR"


class TransactionOut(BaseModel):
    txn_id: str
    owner_id: str
    amount: float
    direction: str
    category: str
    counterparty_phone: str
    counterparty_name: str
    description: str
    txn_date: str
    created_at: str


# --- Accounting ---
class AccountingSummary(BaseModel):
    period: str
    total_inflow: float
    total_outflow: float
    net_cash_flow: float
    transaction_count: int


class PnLReport(BaseModel):
    period: str
    revenue: float
    cost_of_goods: float
    gross_profit: float
    operating_expenses: float
    net_profit: float
    expense_breakdown: dict[str, float]


class CashFlowReport(BaseModel):
    period: str
    operating_inflow: float
    operating_outflow: float
    capital_outflow: float
    net_cash_flow: float


class CategoryBreakdown(BaseModel):
    category: str
    total: float
    count: int
    percentage: float


# --- Score ---
class ScoreComponent(BaseModel):
    name: str
    score: int
    max_score: int
    details: dict


class ScoreResult(BaseModel):
    score_id: str
    owner_id: str
    total_score: int
    tier: str
    components: list[ScoreComponent]
    explanation: str
    generated_at: str


class ScoreHistory(BaseModel):
    scores: list[ScoreResult]


# --- Chat ---
class ChatMessage(BaseModel):
    message: str
    conversation_history: list[dict] = []


class ChatResponse(BaseModel):
    response: str
