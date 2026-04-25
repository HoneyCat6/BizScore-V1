import json
import boto3
from config import settings

_bedrock_client = None


def get_bedrock_client():
    global _bedrock_client
    if _bedrock_client is None:
        kwargs = {"region_name": settings.aws_region}
        if settings.aws_access_key_id:
            kwargs["aws_access_key_id"] = settings.aws_access_key_id
            kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
            if settings.aws_session_token:
                kwargs["aws_session_token"] = settings.aws_session_token
        _bedrock_client = boto3.client("bedrock-runtime", **kwargs)
    return _bedrock_client


def invoke_claude(
    system_prompt: str,
    user_message: str,
    max_tokens: int = 1024,
    conversation_history: list[dict] | None = None,
) -> str:
    client = get_bedrock_client()

    messages = []
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": messages,
    })

    response = client.invoke_model(
        modelId=settings.bedrock_model_id,
        body=body,
        contentType="application/json",
        accept="application/json",
    )

    result = json.loads(response["body"].read())
    return result["content"][0]["text"]
