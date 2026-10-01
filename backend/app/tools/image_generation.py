import logging
from collections.abc import Callable

from PIL import Image

from app.core.config import ImageProvider, get_settings
from app.domain.state import DesignSpec
from app.providers.base import ProviderError
from app.tools.compositor import CANVAS, cover, make_studio_background
from app.tools.image_providers import generate_bedrock_image, generate_openai_image

logger = logging.getLogger(__name__)
PROMPT_LIMIT = 3900
TEXT_SPACE = {
    "left": "Keep the left third dark and uncluttered so a headline can sit there.",
    "right": "Keep the right third dark and uncluttered so a headline can sit there.",
    "center": "Keep the middle band uncluttered so a large headline can sit there.",
}
GENERATORS: dict[ImageProvider, Callable[[str], Image.Image]] = {
    "openai": generate_openai_image,
    "bedrock": generate_bedrock_image,
}


def image_provider_for(privacy_mode: str) -> ImageProvider:
    # Hosted image models would send the prompt off this machine.
    if privacy_mode == "local":
        return "compositor"
    return get_settings().active_image_provider


def render_background(spec: DesignSpec, privacy_mode: str) -> tuple[Image.Image, str]:
    provider = image_provider_for(privacy_mode)
    if provider == "compositor":
        return make_studio_background(spec), "studio-compositor"
    try:
        return cover(GENERATORS[provider](thumbnail_prompt(spec)), *CANVAS), provider
    except ProviderError:
        if privacy_mode == "cloud":
            raise
        logger.warning("%s image generation failed; using the studio compositor", provider)
        return make_studio_background(spec), "studio-compositor"


def thumbnail_prompt(spec: DesignSpec) -> str:
    subject = spec.subject.get("description", "")
    subject_side = "left" if spec.subject.get("position") == "left" else "right"
    parts = [
        spec.image_prompt or str(subject),
        f"Setting: {spec.background['description']}." if spec.background.get("description") else "",
        f"Lighting: {spec.lighting}." if spec.lighting else "",
        f"YouTube thumbnail background, 16:9, main subject large on the {subject_side} side.",
        "Cinematic, bold high-contrast colors, sharp focus, dramatic depth.",
        TEXT_SPACE[spec.text.position],
        "No text, letters, captions, logos, or watermarks.",
    ]
    return " ".join(part for part in parts if part)[:PROMPT_LIMIT]
