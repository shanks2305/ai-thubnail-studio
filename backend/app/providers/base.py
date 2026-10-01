from dataclasses import dataclass


class ProviderError(Exception):
    pass


@dataclass(frozen=True)
class LLMRequest:
    task: str
    system: str
    user: str


@dataclass(frozen=True)
class LLMResponse:
    content: str
    provider: str
    model: str
