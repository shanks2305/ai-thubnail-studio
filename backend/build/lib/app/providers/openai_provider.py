import base64

import httpx

from app.core.config import get_settings
from app.providers.base import LLMRequest, LLMResponse, ProviderError


class OpenAIProvider:
    name = "openai"

    def generate(self, request: LLMRequest) -> LLMResponse:
        settings = get_settings()
        if not settings.openai_api_key:
            raise ProviderError("OPENAI_API_KEY is not set.")
        payload = {
            "model": request.model,
            "temperature": 0.7,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": f"{request.system}\n\nReturn one JSON object. No markdown."},
                {"role": "user", "content": _user_content(request)},
            ],
        }
        try:
            response = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json=payload,
                timeout=90,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
        except httpx.HTTPError as exc:
            raise ProviderError("OpenAI could not complete this step.") from exc
        return LLMResponse(content=content, provider=self.name, model=request.model)


def _user_content(request: LLMRequest) -> str | list[dict[str, object]]:
    if not request.images:
        return request.user
    images = [
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64.b64encode(image).decode()}"}}
        for image in request.images
    ]
    return [{"type": "text", "text": request.user}, *images]
