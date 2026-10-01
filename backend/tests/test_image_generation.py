import base64
import io
import json
from io import BytesIO

import httpx
import pytest
from PIL import Image

from app.core.config import get_settings
from app.domain.state import DesignSpec, TextSpec
from app.providers.base import ProviderError
from app.tools import image_providers
from app.tools.image_generation import render_background, thumbnail_prompt


@pytest.fixture
def settings(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    def configure(**values: str) -> None:
        defaults = {"APP_ENV": "development", "OPENAI_API_KEY": "sk", "IMAGE_PROVIDER": "openai"}
        for key, value in {**defaults, **values}.items():
            monkeypatch.setenv(key, value)
        get_settings.cache_clear()

    yield configure
    get_settings.cache_clear()


def _spec() -> DesignSpec:
    return DesignSpec(
        subject={"position": "right", "description": "a creepy room"},
        background={"description": "an abandoned house"},
        text=TextSpec(content="Room of Horrors", position="left"),
        image_prompt="Cobwebs over old furniture",
    )


def _encoded_png() -> str:
    buffer = BytesIO()
    Image.new("RGB", (1536, 1024), "#331111").save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


def _patch_openai(monkeypatch, handler) -> list[httpx.Request]:
    sent: list[httpx.Request] = []

    def record(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        return handler(request)

    client = httpx.Client(transport=httpx.MockTransport(record))
    monkeypatch.setattr(image_providers.httpx, "post", client.post)
    return sent


class _FakeBedrock:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.calls: list[dict] = []

    def invoke_model(self, **kwargs):
        self.calls.append(kwargs)
        return {"body": io.BytesIO(json.dumps(self.payload).encode())}


def test_openai_image_uses_quality_for_the_environment(settings, monkeypatch):
    settings()
    sent = _patch_openai(monkeypatch, lambda request: httpx.Response(200, json={"data": [{"b64_json": _encoded_png()}]}))
    image, provider = render_background(_spec(), "hybrid")
    assert provider == "openai"
    assert image.size == (1280, 720)
    assert json.loads(sent[0].content)["quality"] == "low"


def test_bedrock_image_requests_a_16_by_9_stability_image(settings, monkeypatch):
    settings(IMAGE_PROVIDER="bedrock")
    fake = _FakeBedrock({"images": [_encoded_png()], "finish_reasons": [None]})
    monkeypatch.setattr(image_providers, "bedrock_runtime", lambda region: fake)
    image, provider = render_background(_spec(), "hybrid")
    assert provider == "bedrock"
    assert image.size == (1280, 720)
    assert fake.calls[0]["modelId"] == "stability.stable-image-core-v1:1"
    assert json.loads(fake.calls[0]["body"])["aspect_ratio"] == "16:9"


def test_filtered_bedrock_image_raises_in_cloud_mode(settings, monkeypatch):
    settings(IMAGE_PROVIDER="bedrock")
    fake = _FakeBedrock({"images": [], "finish_reasons": ["Filter reason: prompt"]})
    monkeypatch.setattr(image_providers, "bedrock_runtime", lambda region: fake)
    with pytest.raises(ProviderError):
        render_background(_spec(), "cloud")


def test_hybrid_falls_back_to_compositor_when_generation_fails(settings, monkeypatch):
    settings()
    _patch_openai(monkeypatch, lambda request: httpx.Response(500))
    _, provider = render_background(_spec(), "hybrid")
    assert provider == "studio-compositor"


def test_prompt_reserves_headline_space_and_forbids_text():
    prompt = thumbnail_prompt(_spec())
    assert "Cobwebs over old furniture" in prompt
    assert "left third" in prompt
    assert "No text" in prompt
