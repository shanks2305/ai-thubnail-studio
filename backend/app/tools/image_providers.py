import base64
import json
from io import BytesIO

import httpx
from botocore.exceptions import BotoCoreError, ClientError
from PIL import Image, UnidentifiedImageError

from app.core.config import get_settings
from app.providers.base import ProviderError
from app.providers.bedrock import bedrock_runtime

OPENAI_IMAGES_URL = "https://api.openai.com/v1/images/generations"
# GPT Image models only accept fixed landscape sizes; callers crop to 1280x720.
OPENAI_IMAGE_SIZE = "1536x1024"
REQUEST_TIMEOUT_SECONDS = 180
NEGATIVE_PROMPT = "text, letters, words, captions, logo, watermark, blurry, low contrast"


def generate_openai_image(prompt: str) -> Image.Image:
    settings = get_settings()
    if not settings.openai_api_key:
        raise ProviderError("OPENAI_API_KEY is not set.")
    try:
        response = httpx.post(
            OPENAI_IMAGES_URL,
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            json={
                "model": settings.openai_image_model,
                "prompt": prompt,
                "size": OPENAI_IMAGE_SIZE,
                "quality": settings.image_quality,
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return _decode(response.json()["data"][0]["b64_json"])
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
        raise ProviderError("OpenAI image generation failed.") from exc


def generate_bedrock_image(prompt: str) -> Image.Image:
    settings = get_settings()
    body = {
        "prompt": prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "aspect_ratio": "16:9",
        "output_format": "png",
    }
    try:
        response = bedrock_runtime(settings.aws_region).invoke_model(
            modelId=settings.bedrock_image_model_id,
            body=json.dumps(body),
        )
        payload = json.loads(response["body"].read())
        reason = (payload.get("finish_reasons") or [None])[0]
        if reason:
            raise ProviderError(f"Bedrock did not return an image ({reason}).")
        return _decode(payload["images"][0])
    except (BotoCoreError, ClientError, KeyError, IndexError, ValueError) as exc:
        raise ProviderError("Bedrock image generation failed.") from exc


def _decode(encoded: str) -> Image.Image:
    try:
        return Image.open(BytesIO(base64.b64decode(encoded))).convert("RGB")
    except UnidentifiedImageError as exc:
        raise ValueError("Image provider returned unreadable data") from exc
