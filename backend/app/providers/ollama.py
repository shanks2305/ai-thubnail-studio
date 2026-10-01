import time

import httpx

from app.core.config import get_settings
from app.providers.base import LLMRequest, LLMResponse, ProviderError

_checked_at = 0.0
_reachable = False


def ollama_reachable() -> bool:
    global _checked_at, _reachable
    now = time.monotonic()
    if now - _checked_at < 15:
        return _reachable
    _checked_at = now
    try:
        response = httpx.get(f"{get_settings().ollama_base_url.rstrip('/')}/api/tags", timeout=0.4)
        _reachable = response.status_code == 200
    except httpx.HTTPError:
        _reachable = False
    return _reachable


def reset_ollama_cache() -> None:
    global _checked_at, _reachable
    _checked_at = 0.0
    _reachable = False


class OllamaProvider:
    name = "ollama"

    def generate(self, request: LLMRequest) -> LLMResponse:
        settings = get_settings()
        payload = {
            "model": settings.ollama_model,
            "stream": False,
            "format": "json",
            "messages": [
                {"role": "system", "content": request.system},
                {"role": "user", "content": request.user},
            ],
        }
        try:
            response = httpx.post(
                f"{settings.ollama_base_url.rstrip('/')}/api/chat",
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            content = response.json()["message"]["content"]
        except httpx.HTTPError as exc:
            raise ProviderError("Ollama could not complete this step.") from exc
        return LLMResponse(content=content, provider=self.name, model=settings.ollama_model)
