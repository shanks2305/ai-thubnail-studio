import json
import logging

from app.core.config import HOSTED_PROVIDERS, TextProvider, get_settings
from app.providers.base import LLMRequest, LLMResponse, ProviderError
from app.providers.bedrock import BedrockProvider
from app.providers.deterministic import DeterministicProvider
from app.providers.ollama import OllamaProvider, ollama_reachable
from app.providers.openai_provider import OpenAIProvider
from app.providers.prompts import load_prompt
from app.tools.image_generation import image_provider_for

logger = logging.getLogger(__name__)

_studio = DeterministicProvider()
_PROVIDERS = {"studio": _studio, "ollama": OllamaProvider(), "openai": OpenAIProvider(), "bedrock": BedrockProvider()}
_TEXT_LABELS = {"studio": "the local studio engine", "ollama": "Ollama", "openai": "OpenAI", "bedrock": "AWS Bedrock"}
_IMAGE_LABELS = {"compositor": "the local compositor", "openai": "OpenAI", "bedrock": "AWS Bedrock"}


class ModelRouter:
    def generate(self, *, task: str, payload: dict, privacy_mode: str) -> LLMResponse:
        provider = _PROVIDERS[text_provider_for(privacy_mode)]
        request = LLMRequest(task=task, system=load_prompt(task), user=json.dumps(payload))
        try:
            return provider.generate(request)
        except ProviderError:
            if provider is _studio or privacy_mode == "cloud":
                raise
            logger.warning("Provider %s failed for %s; using the studio engine", provider.name, task)
            return _studio.generate(request)


def text_provider_for(privacy_mode: str) -> TextProvider:
    provider = get_settings().active_text_provider
    # Local projects never send data to a hosted model.
    if privacy_mode == "local" and provider in HOSTED_PROVIDERS:
        return "ollama" if ollama_reachable() else "studio"
    return provider


def readiness_error(privacy_mode: str) -> str | None:
    if privacy_mode == "local":
        return None
    problems = get_settings().missing_credentials()
    return " ".join(problems) if problems else None


def system_status() -> dict[str, object]:
    settings = get_settings()
    text = settings.active_text_provider
    image = settings.active_image_provider
    return {
        "environment": settings.app_env,
        "text_provider": text,
        "image_provider": image,
        "openai_configured": bool(settings.openai_api_key),
        "ollama_reachable": ollama_reachable() if text == "ollama" else False,
        "message": (
            f"{settings.app_env.capitalize()}: concepts by {_TEXT_LABELS[text]}, "
            f"images by {_IMAGE_LABELS[image]}. Local projects stay on this machine."
        ),
    }
