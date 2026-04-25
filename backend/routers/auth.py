from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, Header
from jose import jwt
from passlib.hash import bcrypt

from config import settings
from dynamo import get_table, TABLE_OWNERS
from schemas.models import RegisterRequest, LoginRequest, TokenResponse, OwnerProfile

router = APIRouter(prefix="/api/auth", tags=["auth"])


def create_token(owner_id: str, phone: str) -> str:
    payload = {
        "sub": owner_id,
        "phone": phone,
        "exp": datetime.now(timezone.utc).timestamp() + settings.jwt_expire_minutes * 60,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_owner_id(authorization: str = Header(...)) -> str:
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest):
    table = get_table(TABLE_OWNERS)

    existing = table.get_item(Key={"phone": req.phone}).get("Item")
    if existing:
        raise HTTPException(status_code=409, detail="Phone number already registered")

    owner_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()

    table.put_item(
        Item={
            "phone": req.phone,
            "owner_id": owner_id,
            "name": req.name,
            "pin_hash": bcrypt.hash(req.pin),
            "business_name": req.business_name,
            "business_type": req.business_type,
            "location": req.location,
            "wallet_balance": 0,
            "created_at": now,
        }
    )

    token = create_token(owner_id, req.phone)
    return TokenResponse(
        access_token=token,
        owner_id=owner_id,
        name=req.name,
        business_name=req.business_name,
    )


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    table = get_table(TABLE_OWNERS)
    item = table.get_item(Key={"phone": req.phone}).get("Item")

    if not item or not bcrypt.verify(req.pin, item["pin_hash"]):
        raise HTTPException(status_code=401, detail="Invalid phone or PIN")

    token = create_token(item["owner_id"], req.phone)
    return TokenResponse(
        access_token=token,
        owner_id=item["owner_id"],
        name=item["name"],
        business_name=item["business_name"],
    )


@router.get("/me", response_model=OwnerProfile)
def get_profile(owner_id: str = Depends(get_current_owner_id)):
    table = get_table(TABLE_OWNERS)
    resp = table.query(
        IndexName="owner_id-index",
        KeyConditionExpression="owner_id = :oid",
        ExpressionAttributeValues={":oid": owner_id},
    )
    items = resp.get("Items", [])
    if not items:
        raise HTTPException(status_code=404, detail="Owner not found")

    item = items[0]
    return OwnerProfile(
        owner_id=item["owner_id"],
        phone=item["phone"],
        name=item["name"],
        business_name=item["business_name"],
        business_type=item["business_type"],
        location=item.get("location", ""),
        wallet_balance=float(item.get("wallet_balance", 0)),
        created_at=item["created_at"],
    )
