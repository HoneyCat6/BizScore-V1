"""Generate realistic demo wallet transaction histories for 8 personas."""
import random
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from uuid import uuid4

from ulid import ULID
from passlib.hash import bcrypt

from dynamo import get_table, TABLE_OWNERS, TABLE_TRANSACTIONS


PERSONAS = [
    {
        "phone": "60123456001",
        "pin": "1234",
        "name": "Maria",
        "business_name": "Maria's Fresh Market",
        "business_type": "Market Vendor",
        "location": "Pasar Besar, Kuala Lumpur",
        "months": 2,
        "daily_sales": (3, 7),
        "sale_amount": (3, 20),
        "customers": 50,
        "expenses": {
            "cost_of_goods": (2, 5, (20, 80)),
            "rent": (1, 1, (300, 300)),
            "utilities": (1, 1, (50, 80)),
            "operating_expense": (1, 2, (15, 50)),
        },
        "growth_factor": 1.03,
        "initial_balance": Decimal("1500"),
    },
    {
        "phone": "60123456002",
        "pin": "1234",
        "name": "James",
        "business_name": "James Ride Service",
        "business_type": "Transport (Boda-boda)",
        "location": "Petaling Jaya, Selangor",
        "months": 1.5,
        "daily_sales": (2, 5),
        "sale_amount": (5, 18),
        "customers": 20,
        "expenses": {
            "operating_expense": (3, 6, (10, 25)),
            "rent": (0, 1, (200, 200)),
            "utilities": (0, 1, (30, 50)),
        },
        "growth_factor": 1.01,
        "initial_balance": Decimal("800"),
    },
    {
        "phone": "60123456003",
        "pin": "1234",
        "name": "Aisha",
        "business_name": "Aisha Tailoring",
        "business_type": "Tailor",
        "location": "Klang, Selangor",
        "months": 1.5,
        "daily_sales": (0, 3),
        "sale_amount": (20, 80),
        "customers": 8,
        "expenses": {
            "cost_of_goods": (1, 2, (15, 50)),
            "rent": (0, 1, (200, 200)),
            "utilities": (0, 1, (30, 50)),
            "other_expense": (0, 1, (10, 25)),
        },
        "growth_factor": 1.05,
        "initial_balance": Decimal("1000"),
    },
    # --- Food Stall Vendors ---
    {
        "phone": "60123456004",
        "pin": "1234",
        "name": "Ahmad",
        "business_name": "Ahmad's Nasi Lemak",
        "business_type": "food_stall",
        "location": "Kuala Lumpur",
        "months": 2,
        "daily_sales": (4, 8),
        "sale_amount": (3, 15),
        "customers": 40,
        "expenses": {
            "cost_of_goods": (3, 6, (20, 60)),
            "rent": (1, 1, (250, 250)),
            "utilities": (1, 1, (40, 60)),
        },
        "growth_factor": 1.02,
        "initial_balance": Decimal("850"),
    },
    {
        "phone": "60123456005",
        "pin": "1234",
        "name": "Siti",
        "business_name": "Siti's Roti Canai",
        "business_type": "food_stall",
        "location": "Penang",
        "months": 1.5,
        "daily_sales": (5, 10),
        "sale_amount": (2, 12),
        "customers": 50,
        "expenses": {
            "cost_of_goods": (3, 7, (15, 50)),
            "rent": (1, 1, (250, 250)),
            "utilities": (1, 1, (40, 60)),
        },
        "growth_factor": 1.02,
        "initial_balance": Decimal("1200"),
    },
    {
        "phone": "60123456006",
        "pin": "1234",
        "name": "Kumar",
        "business_name": "Kumar's Nasi Kandar",
        "business_type": "food_stall",
        "location": "Johor Bahru",
        "months": 1.5,
        "daily_sales": (3, 7),
        "sale_amount": (4, 18),
        "customers": 30,
        "expenses": {
            "cost_of_goods": (2, 5, (20, 60)),
            "rent": (1, 1, (200, 200)),
            "utilities": (1, 1, (35, 55)),
        },
        "growth_factor": 1.01,
        "initial_balance": Decimal("650"),
    },
    # --- Beverage Vendors ---
    {
        "phone": "60123456007",
        "pin": "1234",
        "name": "Mei Ling",
        "business_name": "Mei Ling's Bubble Tea",
        "business_type": "beverage",
        "location": "Kuala Lumpur",
        "months": 1.5,
        "daily_sales": (5, 12),
        "sale_amount": (5, 12),
        "customers": 50,
        "expenses": {
            "cost_of_goods": (3, 6, (30, 80)),
            "rent": (1, 1, (350, 350)),
            "utilities": (1, 1, (50, 80)),
        },
        "growth_factor": 1.03,
        "initial_balance": Decimal("1800"),
    },
    {
        "phone": "60123456008",
        "pin": "1234",
        "name": "Raj",
        "business_name": "Raj's Fresh Juice",
        "business_type": "beverage",
        "location": "Penang",
        "months": 1,
        "daily_sales": (3, 8),
        "sale_amount": (5, 15),
        "customers": 25,
        "expenses": {
            "cost_of_goods": (3, 6, (20, 60)),
            "rent": (1, 1, (200, 200)),
            "utilities": (0, 1, (30, 50)),
        },
        "growth_factor": 1.01,
        "initial_balance": Decimal("500"),
    },
]


# ── Set to True to force-delete and re-seed ALL demo accounts ──────────
FORCE_RESEED = False  # Set to True to wipe and re-seed demo accounts


def _delete_demo_account(phone: str, owners_table, txn_table):
    """Delete a demo owner and all their transactions from DynamoDB."""
    resp = owners_table.get_item(Key={"phone": phone})
    if "Item" not in resp:
        return
    owner_id = resp["Item"]["owner_id"]

    # Delete all transactions belonging to this owner
    txn_resp = txn_table.query(
        KeyConditionExpression="owner_id = :oid",
        ExpressionAttributeValues={":oid": owner_id},
        ProjectionExpression="owner_id, txn_id",
    )
    with txn_table.batch_writer() as batch:
        for item in txn_resp.get("Items", []):
            batch.delete_item(Key={"owner_id": item["owner_id"], "txn_id": item["txn_id"]})
    # Handle pagination
    while txn_resp.get("LastEvaluatedKey"):
        txn_resp = txn_table.query(
            KeyConditionExpression="owner_id = :oid",
            ExpressionAttributeValues={":oid": owner_id},
            ProjectionExpression="owner_id, txn_id",
            ExclusiveStartKey=txn_resp["LastEvaluatedKey"],
        )
        with txn_table.batch_writer() as batch:
            for item in txn_resp.get("Items", []):
                batch.delete_item(Key={"owner_id": item["owner_id"], "txn_id": item["txn_id"]})

    # Delete the owner record
    owners_table.delete_item(Key={"phone": phone})
    print(f"  Deleted existing account: {phone}")


def seed_personas():
    """Create demo personas with realistic transaction histories (idempotent)."""
    owners_table = get_table(TABLE_OWNERS)
    txn_table = get_table(TABLE_TRANSACTIONS)

    # ── Force re-seed: delete existing demo accounts first ──────────────
    if FORCE_RESEED:
        print("FORCE_RESEED enabled – deleting existing demo accounts…")
        for persona in PERSONAS:
            _delete_demo_account(persona["phone"], owners_table, txn_table)
        print("Existing demo data cleared.\n")

    for persona in PERSONAS:
        # Skip accounts that already exist
        response = owners_table.get_item(Key={"phone": persona["phone"]})
        if "Item" in response:
            print(f"Account {persona['phone']} ({persona['name']}) already exists. Skipping.")
            continue

        print(f"Seeding account: {persona['name']} ({persona['phone']})")
        persona_to_seed = persona  # noqa

    # Now seed all personas that don't exist yet
    for persona in PERSONAS:
        response = owners_table.get_item(Key={"phone": persona["phone"]})
        if "Item" in response:
            continue

        owner_id = str(uuid4())
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=int(persona["months"] * 30))

        # Create owner
        initial_bal = persona.get("initial_balance", Decimal("1000"))

        owners_table.put_item(Item={
            "phone": persona["phone"],
            "owner_id": owner_id,
            "name": persona["name"],
            "pin_hash": bcrypt.hash(persona["pin"]),
            "business_name": persona["business_name"],
            "business_type": persona["business_type"],
            "location": persona["location"],
            "wallet_balance": initial_bal,
            "created_at": start_date.isoformat(),
        })

        # Generate customer names
        customer_names = [f"Customer_{i:03d}" for i in range(persona["customers"])]
        customer_phones = [f"6019{random.randint(1000000, 9999999)}" for _ in range(persona["customers"])]

        # Generate transactions day by day
        current = start_date
        month_idx = 0
        balance = initial_bal

        with txn_table.batch_writer() as batch:
            while current < now:
                day_of_week = current.weekday()
                # Skip some days randomly (more skips for less active personas)
                if random.random() < 0.15:
                    current += timedelta(days=1)
                    continue

                # Monthly growth factor
                months_elapsed = (current - start_date).days / 30
                growth = persona["growth_factor"] ** months_elapsed

                # --- Sales (inflows) ---
                num_sales = random.randint(*persona["daily_sales"])
                num_sales = int(num_sales * growth)

                for _ in range(num_sales):
                    cust_idx = random.randint(0, len(customer_names) - 1)
                    amount = round(random.uniform(*persona["sale_amount"]) * growth, 2)
                    txn_time = current + timedelta(
                        hours=random.randint(7, 19),
                        minutes=random.randint(0, 59),
                    )

                    batch.put_item(Item={
                        "owner_id": owner_id,
                        "txn_id": str(ULID()),
                        "amount": Decimal(str(amount)),
                        "direction": "inflow",
                        "category": "sales_revenue",
                        "counterparty_phone": customer_phones[cust_idx],
                        "counterparty_name": customer_names[cust_idx],
                        "description": f"Sale",
                        "txn_date": txn_time.isoformat(),
                        "created_at": txn_time.isoformat(),
                    })
                    balance += Decimal(str(amount))

                # --- Expenses (outflows) ---
                for cat, (min_per_month, max_per_month, amount_range) in persona["expenses"].items():
                    # Distribute expenses across the month
                    monthly_count = random.randint(min_per_month, max_per_month)
                    daily_chance = monthly_count / 30

                    if random.random() < daily_chance:
                        amount = round(random.uniform(*amount_range), 2)
                        txn_time = current + timedelta(
                            hours=random.randint(8, 18),
                            minutes=random.randint(0, 59),
                        )

                        batch.put_item(Item={
                            "owner_id": owner_id,
                            "txn_id": str(ULID()),
                            "amount": Decimal(str(amount)),
                            "direction": "outflow",
                            "category": cat,
                            "counterparty_phone": "",
                            "counterparty_name": f"Supplier ({cat})",
                            "description": f"{cat.replace('_', ' ').title()} payment",
                            "txn_date": txn_time.isoformat(),
                            "created_at": txn_time.isoformat(),
                        })
                        balance -= Decimal(str(amount))

                current += timedelta(days=1)

        # Update final balance
        owners_table.update_item(
            Key={"phone": persona["phone"]},
            UpdateExpression="SET wallet_balance = :b",
            ExpressionAttributeValues={":b": max(balance, Decimal("0"))},
        )

        print(f"Seeded {persona['name']} ({persona['business_name']}) - owner_id: {owner_id}")

    print("\nDemo accounts:")
    for p in PERSONAS:
        print(f"  Phone: {p['phone']}, PIN: {p['pin']} — {p['name']} ({p['business_name']})")


if __name__ == "__main__":
    seed_personas()
