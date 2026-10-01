import json
import logging

from app.core.config import AgentRole, get_settings
from app.providers.base import LLMRequest, LLMResponse, ProviderError
from app.providers.bedrock import BedrockProvider
from app.providers.deterministic import DeterministicProvider
from app.providers.ollama import OllamaProvider, ollama_reachable
from app.providers.openai_provider import OpenAIProvider
from app.providers.prompts import load_prompt

logger = logging.getLogger(__name__)

_studio = DeterministicProvider()
_PROVIDERS = {"studio": _studio, "ollama": OllamaProvider(), "openai": OpenAIProvider(), "bedrock": BedrockProvider()}
_CHAT_LABELS = {"studio": "the local studio engine", "ollama": "Ollama", "openai": "OpenAI", "bedrock": "AWS Bedrock"}
_JUDGE_LABELS = {**_CHAT_LABELS, "studio": "built-in pixel checks"}
_IMAGE_LABELS = {"compositor": "the local compositor", "ollama": "Ollama", "openai": "OpenAI", "bedrock": "AWS Bedrock"}
JUDGE_AGENTS = {"critic"}


def role_for(task: str) -> AgentRole:
    return "judge" if task in JUDGE_AGENTS else "chat"


class ModelRouter:
    def generate(self, *, task: str, payload: dict, images: tuple[bytes, ...] = ()) -> LLMResponse:
        settings = get_settings()
        role = role_for(task)
        provider = _PROVIDERS[settings.provider_for(role)]
        request = LLMRequest(
            task=task,
            model=settings.model_for(role),
            system=load_prompt(task),
            user=json.dumps(payload),
            images=images,
        )
        try:
            return provider.generate(request)
        except ProviderError:
            # The studio engine only writes chat steps; the judge falls back in its own module.
            if settings.is_production or role == "judge" or provider is _studio:
                raise
            logger.warning("Provider %s failed for %s; using the studio engine", provider.name, task)
            return _studio.generate(request)


def readiness_error() -> str | None:
    problems = get_settings().missing_credentials()
    return " ".join(problems) if problems else None


def system_status() -> dict[str, object]:
    settings = get_settings()
    chat = settings.provider_for("chat")
    judge = settings.provider_for("judge")
    image = settings.active_image_provider
    return {
        "environment": settings.app_env,
        "chat_provider": chat,
        "judge_provider": judge,
        "image_provider": image,
        "openai_configured": bool(settings.openai_api_key),
        "ollama_reachable": ollama_reachable() if "ollama" in {chat, judge, image} else False,
        "message": (
            f"{settings.app_env.capitalize()}: concepts by {_CHAT_LABELS[chat]}, "
            f"judging by {_JUDGE_LABELS[judge]}, images by {_IMAGE_LABELS[image]}."
        ),
    }
