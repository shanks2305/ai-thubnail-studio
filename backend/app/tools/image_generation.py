import logging
from collections.abc import Callable

from PIL import Image

from app.core.config import ImageProvider, get_settings
from app.domain.state import DesignSpec
from app.domain.styles import style_prompt
from app.providers.base import ProviderError
from app.tools.compositor import CANVAS, cover, make_studio_background
from app.tools.image_providers import generate_bedrock_image, generate_ollama_image, generate_openai_image

logger = logging.getLogger(__name__)
PROMPT_LIMIT = 3900
TEXT_SPACE = {
    "left": "Keep the left third dark and uncluttered so a headline can sit there.",
    "right": "Keep the right third dark and uncluttered so a headline can sit there.",
    "center": "Keep the middle band uncluttered so a large headline can sit there.",
}
GENERATORS: dict[ImageProvider, Callable[[str], Image.Image]] = {
    "ollama": generate_ollama_image,
    "openai": generate_openai_image,
    "bedrock": generate_bedrock_image,
}


def render_background(spec: DesignSpec) -> tuple[Image.Image, str]:
    settings = get_settings()
    provider: ImageProvider = settings.active_image_provider
    if provider == "compositor":
        return make_studio_background(spec), "studio-compositor"
    try:
        return cover(GENERATORS[provider](thumbnail_prompt(spec)), *CANVAS), provider
    except ProviderError:
        if settings.is_production:
            raise
        logger.warning("%s image generation failed; using the studio compositor", provider)
        return make_studio_background(spec), "studio-compositor"


def thumbnail_prompt(spec: DesignSpec) -> str:
    subject = spec.subject.get("description", "")
    subject_side = "left" if spec.subject.get("position") == "left" else "right"
    parts = [
        style_prompt(str(spec.subject.get("style") or "cinematic")),
        spec.image_prompt or str(subject),
        f"Setting: {spec.background['description']}." if spec.background.get("description") else "",
        f"Lighting: {spec.lighting}." if spec.lighting else "",
        TEXT_SPACE[spec.text.position],
        "No text, letters, captions, logos, or watermarks.",
    ]
    if spec.subject.get("portrait"):
        parts.append(
            f"Keep the {subject_side} side empty. A real photo of the creator or people from the video will be placed there. Do not draw a person."
        )
    else:
        parts.append(f"YouTube thumbnail, 16:9, one large subject on the {subject_side} side.")
    if spec.palette:
        parts.append(f"Color grade toward {', '.join(str(color) for color in spec.palette[:3])}.")
    return " ".join(part for part in parts if part)[:PROMPT_LIMIT]
