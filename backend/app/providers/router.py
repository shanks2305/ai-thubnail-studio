import json
import logging

from app.core.config import get_settings
from app.providers.base import LLMRequest, LLMResponse, ProviderError
from app.providers.deterministic import DeterministicProvider
from app.providers.ollama import OllamaProvider, ollama_reachable
from app.providers.openai_provider import OpenAIProvider
from app.providers.prompts import load_prompt

logger = logging.getLogger(__name__)

_deterministic = DeterministicProvider()
_openai = OpenAIProvider()
_ollama = OllamaProvider()


class ModelRouter:
    def generate(self, *, task: str, payload: dict, privacy_mode: str) -> LLMResponse:
        provider = self._choose(privacy_mode)
        request = LLMRequest(task=task, system=load_prompt(task), user=json.dumps(payload))
        try:
            return provider.generate(request)
        except ProviderError:
            if provider is _deterministic or privacy_mode == "cloud" or get_settings().llm_mode != "auto":
                raise
            logger.warning("Provider %s failed for %s; using the studio engine", provider.name, task)
            return _deterministic.generate(request)

    def _choose(self, privacy_mode: str):
        settings = get_settings()
        if settings.llm_mode == "deterministic":
            return _deterministic
        if settings.llm_mode == "openai":
            return _openai
        if settings.llm_mode == "ollama":
            return _ollama
        if privacy_mode == "local":
            return _ollama if ollama_reachable() else _deterministic
        if privacy_mode == "cloud":
            if not settings.openai_api_key:
                raise ProviderError("Cloud mode needs an OpenAI API key.")
            return _openai
        if settings.openai_api_key:
            return _openai
        if ollama_reachable():
            return _ollama
        return _deterministic


def readiness_error(privacy_mode: str) -> str | None:
    settings = get_settings()
    if settings.llm_mode == "deterministic":
        return None
    if settings.llm_mode == "openai" and not settings.openai_api_key:
        return "Set OPENAI_API_KEY or switch the model mode."
    if privacy_mode == "cloud" and settings.llm_mode == "auto" and not settings.openai_api_key:
        return "Cloud mode needs an OpenAI API key. Choose Hybrid or Local, or set OPENAI_API_KEY."
    return None


def system_status() -> dict[str, object]:
    settings = get_settings()
    ollama = ollama_reachable() if settings.llm_mode in {"auto", "ollama"} else False
    openai_ready = bool(settings.openai_api_key) and settings.llm_mode in {"auto", "openai"}
    if settings.llm_mode == "deterministic":
        text_provider = "studio-engine"
        message = "Concepts are written by the local studio engine."
    elif openai_ready:
        text_provider = "openai"
        message = "OpenAI is used for Hybrid and Cloud projects. Local projects stay on this machine."
    elif ollama or settings.llm_mode == "ollama":
        text_provider = "ollama"
        message = f"Ollama ({settings.ollama_model}) can write concepts. Layouts are rendered here."
    else:
        text_provider = "studio-engine"
        message = "No language model is connected. Concepts use the local studio engine."
    image_provider = "openai" if openai_ready else "studio-compositor"
    return {
        "text_provider": text_provider,
        "image_provider": image_provider,
        "openai_configured": bool(settings.openai_api_key),
        "ollama_reachable": ollama,
        "message": message,
    }
