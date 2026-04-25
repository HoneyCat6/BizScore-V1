from datetime import datetime, timezone
from decimal import Decimal

from boto3.dynamodb.conditions import Key
from ulid import ULID

from dynamo import get_table, TABLE_OWNERS, TABLE_TRANSACTIONS
from schemas.models import INFLOW_CATEGORY


class WalletService:
    @staticmethod
    def get_balance(owner_id: str) -> float:
        table = get_table(TABLE_OWNERS)
        resp = table.query(
            IndexName="owner_id-index",
            KeyConditionExpression="owner_id = :oid",
            ExpressionAttributeValues={":oid": owner_id},
        )
        items = resp.get("Items", [])
        if not items:
            return 0.0
        return float(items[0].get("wallet_balance", 0))

    @staticmethod
    def _get_owner_by_id(owner_id: str) -> dict | None:
        table = get_table(TABLE_OWNERS)
        resp = table.query(
            IndexName="owner_id-index",
            KeyConditionExpression="owner_id = :oid",
            ExpressionAttributeValues={":oid": owner_id},
        )
        items = resp.get("Items", [])
        return items[0] if items else None

    @staticmethod
    def _get_owner_by_phone(phone: str) -> dict | None:
        table = get_table(TABLE_OWNERS)
        item = table.get_item(Key={"phone": phone}).get("Item")
        return item

    @staticmethod
    def _update_balance(phone: str, delta: float):
        table = get_table(TABLE_OWNERS)
        table.update_item(
            Key={"phone": phone},
            UpdateExpression="SET wallet_balance = wallet_balance + :d",
            ExpressionAttributeValues={":d": Decimal(str(delta))},
        )

    @staticmethod
    def _record_transaction(
        owner_id: str,
        amount: float,
        direction: str,
        category: str,
        counterparty_phone: str = "",
        counterparty_name: str = "",
        description: str = "",
    ) -> dict:
        table = get_table(TABLE_TRANSACTIONS)
        now = datetime.now(timezone.utc).isoformat()
        txn_id = str(ULID())

        item = {
            "owner_id": owner_id,
            "txn_id": txn_id,
            "amount": Decimal(str(amount)),
            "direction": direction,
            "category": category,
            "counterparty_phone": counterparty_phone,
            "counterparty_name": counterparty_name,
            "description": description,
            "txn_date": now,
            "created_at": now,
        }
        table.put_item(Item=item)
        # Convert Decimal to float for response
        item["amount"] = float(item["amount"])
        return item

    @classmethod
    def topup(cls, owner_id: str, amount: float) -> dict:
        owner = cls._get_owner_by_id(owner_id)
        if not owner:
            raise ValueError("Owner not found")

        cls._update_balance(owner["phone"], amount)
        return cls._record_transaction(
            owner_id=owner_id,
            amount=amount,
            direction="inflow",
            category="topup",
            description="Wallet top-up",
        )

    @classmethod
    def send_payment(
        cls,
        owner_id: str,
        amount: float,
        recipient_phone: str,
        category: str,
        description: str = "",
    ) -> dict:
        owner = cls._get_owner_by_id(owner_id)
        if not owner:
            raise ValueError("Owner not found")

        balance = float(owner.get("wallet_balance", 0))
        if balance < amount:
            raise ValueError("Insufficient balance")

        # Deduct from sender
        cls._update_balance(owner["phone"], -amount)

        # Credit recipient if they exist in the system
        recipient = cls._get_owner_by_phone(recipient_phone)
        recipient_name = ""
        if recipient:
            cls._update_balance(recipient_phone, amount)
            recipient_name = recipient.get("name", "")
            # Record inflow for recipient (auto-categorized as sales)
            cls._record_transaction(
                owner_id=recipient["owner_id"],
                amount=amount,
                direction="inflow",
                category=INFLOW_CATEGORY,
                counterparty_phone=owner["phone"],
                counterparty_name=owner.get("name", ""),
                description=description,
            )

        # Record outflow for sender
        return cls._record_transaction(
            owner_id=owner_id,
            amount=amount,
            direction="outflow",
            category=category,
            counterparty_phone=recipient_phone,
            counterparty_name=recipient_name,
            description=description,
        )

    @classmethod
    def receive_payment(
        cls,
        owner_id: str,
        amount: float,
        payer_phone: str = "",
        payer_name: str = "",
        description: str = "",
    ) -> dict:
        """Simulate receiving a payment (e.g., customer scanned QR)."""
        owner = cls._get_owner_by_id(owner_id)
        if not owner:
            raise ValueError("Owner not found")

        # Credit the owner
        cls._update_balance(owner["phone"], amount)

        # Auto-categorized as sales_revenue
        return cls._record_transaction(
            owner_id=owner_id,
            amount=amount,
            direction="inflow",
            category=INFLOW_CATEGORY,
            counterparty_phone=payer_phone,
            counterparty_name=payer_name,
            description=description,
        )

    @classmethod
    def get_transactions(
        cls,
        owner_id: str,
        start_date: str | None = None,
        end_date: str | None = None,
        category: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        table = get_table(TABLE_TRANSACTIONS)

        if start_date and end_date:
            resp = table.query(
                IndexName="owner-date-index",
                KeyConditionExpression=Key("owner_id").eq(owner_id)
                & Key("txn_date").between(start_date, end_date),
                ScanIndexForward=False,
                Limit=limit,
            )
        else:
            resp = table.query(
                KeyConditionExpression=Key("owner_id").eq(owner_id),
                ScanIndexForward=False,
                Limit=limit,
            )

        items = resp.get("Items", [])
        # Convert Decimal to float
        for item in items:
            item["amount"] = float(item["amount"])

        if category:
            items = [i for i in items if i.get("category") == category]

        return items
