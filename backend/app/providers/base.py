from dataclasses import dataclass


class ProviderError(Exception):
    pass


@dataclass(frozen=True)
class LLMRequest:
    task: str
    model: str
    system: str
    user: str
    # PNG bytes sent with the user message; only vision models accept these.
    images: tuple[bytes, ...] = ()


@dataclass(frozen=True)
class LLMResponse:
    content: str
    provider: str
    model: str
