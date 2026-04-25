import io
import qrcode
import urllib.parse
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse

from routers.auth import get_current_owner_id
from services.wallet_service import WalletService
from schemas.models import (
    TopUpRequest,
    SendPaymentRequest,
    ReceivePaymentRequest,
    WalletBalance,
    TransactionOut,
)

router = APIRouter(prefix="/api/wallet", tags=["wallet"])


@router.get("/balance", response_model=WalletBalance)
def get_balance(owner_id: str = Depends(get_current_owner_id)):
    balance = WalletService.get_balance(owner_id)
    return WalletBalance(balance=balance)


@router.post("/topup", response_model=TransactionOut)
def topup(req: TopUpRequest, owner_id: str = Depends(get_current_owner_id)):
    try:
        txn = WalletService.topup(owner_id, req.amount)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return TransactionOut(**txn)


@router.post("/send", response_model=TransactionOut)
def send_payment(req: SendPaymentRequest, owner_id: str = Depends(get_current_owner_id)):
    try:
        txn = WalletService.send_payment(
            owner_id=owner_id,
            amount=req.amount,
            recipient_phone=req.recipient_phone,
            category=req.category.value,
            description=req.description,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return TransactionOut(**txn)


@router.post("/receive", response_model=TransactionOut)
def receive_payment(req: ReceivePaymentRequest, owner_id: str = Depends(get_current_owner_id)):
    try:
        txn = WalletService.receive_payment(
            owner_id=owner_id,
            amount=req.amount,
            payer_phone=req.payer_phone,
            payer_name=req.payer_name,
            description=req.description,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return TransactionOut(**txn)


@router.get("/qr")
def get_qr_code(owner_id: str = Depends(get_current_owner_id), amount: float = Query(None)):
    """Generate a QR code containing a payment link for this business."""
    owner = WalletService._get_owner_by_id(owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")

    params = {"phone": owner["phone"], "name": owner.get("business_name", "")}
    if amount is not None:
        params["amount"] = amount
    qr_data = "bizscore://pay?" + urllib.parse.urlencode(params)
    img = qrcode.make(qr_data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
