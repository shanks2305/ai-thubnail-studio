import json

from app.providers.base import LLMRequest, LLMResponse
from app.providers.studio_engine import run_task


class DeterministicProvider:
    name = "studio-engine"

    def generate(self, request: LLMRequest) -> LLMResponse:
        payload = json.loads(request.user)
        content = json.dumps(run_task(request.task, payload))
        return LLMResponse(content=content, provider=self.name, model="local-studio")
