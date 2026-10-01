import base64
import logging
from io import BytesIO

import httpx
from PIL import Image

from app.core.config import get_settings
from app.domain.state import DesignSpec
from app.providers.base import ProviderError
from app.tools.compositor import cover, make_studio_background

logger = logging.getLogger(__name__)
CANVAS = (1280, 720)


def render_background(spec: DesignSpec, privacy_mode: str) -> tuple[Image.Image, str]:
    settings = get_settings()
    allow_cloud = privacy_mode in {"hybrid", "cloud"} and settings.llm_mode in {"auto", "openai"}
    if allow_cloud and settings.openai_api_key:
        try:
            return _openai_image(spec.image_prompt), "openai"
        except ProviderError:
            if privacy_mode == "cloud":
                raise
            logger.warning("OpenAI image generation failed; using the studio compositor")
    return make_studio_background(spec), "studio-compositor"


def _openai_image(prompt: str) -> Image.Image:
    settings = get_settings()
    try:
        response = httpx.post(
            "https://api.openai.com/v1/images/generations",
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            json={
                "model": settings.openai_image_model,
                "prompt": prompt[:3900],
                "size": "1792x1024",
                "response_format": "b64_json",
            },
            timeout=180,
        )
        response.raise_for_status()
        encoded = response.json()["data"][0]["b64_json"]
    except (httpx.HTTPError, KeyError, IndexError) as exc:
        raise ProviderError("Image generation failed.") from exc
    image = Image.open(BytesIO(base64.b64decode(encoded))).convert("RGB")
    return cover(image, *CANVAS)
