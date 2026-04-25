from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # AWS
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_session_token: Optional[str] = None  # Only needed for temporary STS credentials
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "anthropic.claude-3-haiku-20240307"

    # DynamoDB
    dynamodb_table_prefix: str = "bizscore"
    dynamodb_endpoint_url: str | None = None  # For local DynamoDB

    # JWT
    jwt_secret: str = "bizscore-hackathon-secret-change-in-prod"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours

    # App
    app_name: str = "BizScore"
    debug: bool = True

    model_config = {"env_file": "../.env", "env_file_encoding": "utf-8"}


settings = Settings()
