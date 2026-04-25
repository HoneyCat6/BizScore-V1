"""Generate realistic demo wallet transaction histories for 3 personas."""
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
        "months": 6,
        "daily_sales": (12, 20),
        "sale_amount": (5, 80),
        "customers": 200,
        "expenses": {
            "cost_of_goods": (3, 8, (50, 300)),
            "rent": (1, 1, (500, 500)),
            "utilities": (1, 2, (80, 150)),
            "salary": (1, 2, (800, 1200)),
            "operating_expense": (1, 3, (20, 100)),
        },
        "growth_factor": 1.03,
    },
    {
        "phone": "60123456002",
        "pin": "1234",
        "name": "James",
        "business_name": "James Ride Service",
        "business_type": "Transport (Boda-boda)",
        "location": "Petaling Jaya, Selangor",
        "months": 3,
        "daily_sales": (3, 8),
        "sale_amount": (8, 25),
        "customers": 40,
        "expenses": {
            "operating_expense": (5, 10, (15, 40)),
            "rent": (0, 1, (300, 300)),
            "utilities": (0, 1, (50, 80)),
        },
        "growth_factor": 1.01,
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
        "sale_amount": (30, 150),
        "customers": 8,
        "expenses": {
            "cost_of_goods": (1, 3, (20, 80)),
            "rent": (0, 1, (250, 250)),
            "utilities": (0, 1, (40, 60)),
            "other_expense": (0, 2, (10, 30)),
        },
        "growth_factor": 1.05,
    },
]


def seed_personas():
    """Create demo personas with realistic transaction histories (idempotent)."""
    owners_table = get_table(TABLE_OWNERS)
    txn_table = get_table(TABLE_TRANSACTIONS)

    # Check if any demo accounts already exist
    for persona in PERSONAS:
        response = owners_table.get_item(Key={"phone": persona["phone"]})
        if "Item" in response:
            print("Demo accounts already seeded. Skipping.")
            return

    for persona in PERSONAS:
        owner_id = str(uuid4())
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=int(persona["months"] * 30))

        # Create owner
        owners_table.put_item(Item={
            "phone": persona["phone"],
            "owner_id": owner_id,
            "name": persona["name"],
            "pin_hash": bcrypt.hash(persona["pin"]),
            "business_name": persona["business_name"],
            "business_type": persona["business_type"],
            "location": persona["location"],
            "wallet_balance": Decimal("10000"),
            "created_at": start_date.isoformat(),
        })

        # Generate customer names
        customer_names = [f"Customer_{i:03d}" for i in range(persona["customers"])]
        customer_phones = [f"6019{random.randint(1000000, 9999999)}" for _ in range(persona["customers"])]

        # Generate transactions day by day
        current = start_date
        month_idx = 0
        balance = Decimal("10000")

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
