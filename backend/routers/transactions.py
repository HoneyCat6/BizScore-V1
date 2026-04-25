from fastapi import APIRouter, Depends, Query

from routers.auth import get_current_owner_id
from services.wallet_service import WalletService
from schemas.models import TransactionOut

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionOut])
def list_transactions(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    category: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    owner_id: str = Depends(get_current_owner_id),
):
    txns = WalletService.get_transactions(
        owner_id=owner_id,
        start_date=start_date,
        end_date=end_date,
        category=category,
        limit=limit,
    )
    return [TransactionOut(**t) for t in txns]


@router.get("/{txn_id}", response_model=TransactionOut)
def get_transaction(txn_id: str, owner_id: str = Depends(get_current_owner_id)):
    from dynamo import get_table, TABLE_TRANSACTIONS

    table = get_table(TABLE_TRANSACTIONS)
    resp = table.get_item(Key={"owner_id": owner_id, "txn_id": txn_id})
    item = resp.get("Item")
    if not item:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Transaction not found")
    item["amount"] = float(item["amount"])
    return TransactionOut(**item)
