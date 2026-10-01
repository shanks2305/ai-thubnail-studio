from functools import lru_cache

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import get_settings
from app.providers.base import LLMRequest, LLMResponse, ProviderError

# Image models can take well over the default 60s read timeout.
_CLIENT_CONFIG = Config(read_timeout=300, retries={"max_attempts": 3, "mode": "standard"})


@lru_cache
def bedrock_runtime(region: str):
    """Credentials come from the standard AWS chain (env vars, profile, or IAM role)."""
    return boto3.client("bedrock-runtime", region_name=region, config=_CLIENT_CONFIG)


class BedrockProvider:
    name = "bedrock"

    def generate(self, request: LLMRequest) -> LLMResponse:
        if not request.model:
            raise ProviderError("No Bedrock model is configured for this step.")
        content: list[dict[str, object]] = [{"text": request.user}]
        content.extend({"image": {"format": "png", "source": {"bytes": image}}} for image in request.images)
        try:
            response = bedrock_runtime(get_settings().aws_region).converse(
                modelId=request.model,
                system=[{"text": f"{request.system}\n\nReturn one JSON object. No markdown."}],
                messages=[{"role": "user", "content": content}],
                inferenceConfig={"temperature": 0.7},
            )
            text = response["output"]["message"]["content"][0]["text"]
        except (BotoCoreError, ClientError, KeyError, IndexError) as exc:
            raise ProviderError("Bedrock could not complete this step.") from exc
        return LLMResponse(content=text, provider=self.name, model=request.model)
