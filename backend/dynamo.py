import boto3
from config import settings

_dynamodb_resource = None


def get_dynamodb():
    global _dynamodb_resource
    if _dynamodb_resource is None:
        kwargs = {
            "region_name": settings.aws_region,
        }
        if settings.aws_access_key_id:
            kwargs["aws_access_key_id"] = settings.aws_access_key_id
            kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
            if settings.aws_session_token:
                kwargs["aws_session_token"] = settings.aws_session_token
        if settings.dynamodb_endpoint_url:
            kwargs["endpoint_url"] = settings.dynamodb_endpoint_url
        _dynamodb_resource = boto3.resource("dynamodb", **kwargs)
    return _dynamodb_resource


def table_name(suffix: str) -> str:
    return f"{settings.dynamodb_table_prefix}-{suffix}"


def get_table(suffix: str):
    return get_dynamodb().Table(table_name(suffix))


TABLE_OWNERS = "owners"
TABLE_TRANSACTIONS = "transactions"
TABLE_SCORES = "scores"


def create_tables():
    """Create all DynamoDB tables if they don't exist. Idempotent."""
    db = get_dynamodb()
    existing = [t.name for t in db.tables.all()]

    # --- owners ---
    tname = table_name(TABLE_OWNERS)
    if tname not in existing:
        db.create_table(
            TableName=tname,
            KeySchema=[{"AttributeName": "phone", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "phone", "AttributeType": "S"},
                {"AttributeName": "owner_id", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "owner_id-index",
                    "KeySchema": [
                        {"AttributeName": "owner_id", "KeyType": "HASH"}
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )

    # --- transactions ---
    tname = table_name(TABLE_TRANSACTIONS)
    if tname not in existing:
        db.create_table(
            TableName=tname,
            KeySchema=[
                {"AttributeName": "owner_id", "KeyType": "HASH"},
                {"AttributeName": "txn_id", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "owner_id", "AttributeType": "S"},
                {"AttributeName": "txn_id", "AttributeType": "S"},
                {"AttributeName": "txn_date", "AttributeType": "S"},
                {"AttributeName": "category", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "owner-date-index",
                    "KeySchema": [
                        {"AttributeName": "owner_id", "KeyType": "HASH"},
                        {"AttributeName": "txn_date", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
                {
                    "IndexName": "owner-category-index",
                    "KeySchema": [
                        {"AttributeName": "owner_id", "KeyType": "HASH"},
                        {"AttributeName": "category", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )

    # --- scores ---
    tname = table_name(TABLE_SCORES)
    if tname not in existing:
        db.create_table(
            TableName=tname,
            KeySchema=[
                {"AttributeName": "owner_id", "KeyType": "HASH"},
                {"AttributeName": "generated_at", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "owner_id", "AttributeType": "S"},
                {"AttributeName": "generated_at", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
