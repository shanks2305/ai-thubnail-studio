import base64
import json

import httpx
import pytest

from app.core.config import get_settings
from app.providers import ollama, openai_provider
from app.providers.router import ModelRouter, role_for

PNG = b"\x89PNG fake"


@pytest.fixture
def configure(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    def apply(**values: str) -> None:
        for key, value in values.items():
            monkeypatch.setenv(key, value)
        get_settings.cache_clear()

    yield apply
    get_settings.cache_clear()


def _capture(monkeypatch, module, body: dict) -> list[dict]:
    sent: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(json.loads(request.content))
        return httpx.Response(200, json=body)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    monkeypatch.setattr(module.httpx, "post", client.post)
    return sent


def test_critic_is_the_only_judge_agent():
    assert role_for("critic") == "judge"
    assert role_for("creative_director") == "chat"


def test_each_role_uses_its_own_ollama_model(configure, monkeypatch):
    configure(APP_ENV="development", CHAT_PROVIDER="ollama", JUDGE_PROVIDER="ollama")
    sent = _capture(monkeypatch, ollama, {"message": {"content": "{}"}})
    ModelRouter().generate(task="hook_strategist", payload={})
    ModelRouter().generate(task="critic", payload={}, images=(PNG,))
    assert sent[0]["model"] == "llama3.2"
    assert "images" not in sent[0]["messages"][1]
    assert sent[1]["model"] == "qwen2.5vl"
    assert sent[1]["messages"][1]["images"] == [base64.b64encode(PNG).decode()]


def test_openai_judge_sends_the_image_as_a_data_url(configure, monkeypatch):
    configure(APP_ENV="development", JUDGE_PROVIDER="openai", OPENAI_API_KEY="sk", OPENAI_JUDGE_MODEL="gpt-4o")
    sent = _capture(monkeypatch, openai_provider, {"choices": [{"message": {"content": "{}"}}]})
    response = ModelRouter().generate(task="critic", payload={}, images=(PNG,))
    content = sent[0]["messages"][1]["content"]
    assert response.model == "gpt-4o"
    assert content[1]["image_url"]["url"].startswith("data:image/png;base64,")


def test_development_chat_falls_back_to_the_studio_engine(configure, monkeypatch):
    configure(APP_ENV="development", CHAT_PROVIDER="ollama")
    client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(500)))
    monkeypatch.setattr(ollama.httpx, "post", client.post)
    response = ModelRouter().generate(task="hook_strategist", payload={"description": "Trains at night"})
    assert response.provider == "studio-engine"
