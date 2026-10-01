import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings

PROVIDER_ENV = (
    "APP_ENV",
    "CHAT_PROVIDER",
    "JUDGE_PROVIDER",
    "IMAGE_PROVIDER",
    "OPENAI_API_KEY",
    "BEDROCK_CHAT_MODEL",
    "BEDROCK_JUDGE_MODEL",
    "OPENAI_IMAGE_QUALITY",
)
HOSTED = {"CHAT_PROVIDER": "openai", "JUDGE_PROVIDER": "openai", "IMAGE_PROVIDER": "openai", "OPENAI_API_KEY": "sk"}


@pytest.fixture
def env(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)  # keep backend/.env out of these tests
    for key in PROVIDER_ENV:
        monkeypatch.delenv(key, raising=False)

    def configure(**values: str) -> Settings:
        for key, value in values.items():
            monkeypatch.setenv(key, value)
        get_settings.cache_clear()
        return get_settings()

    yield configure
    get_settings.cache_clear()


def test_development_runs_every_role_locally(env):
    settings = env()
    assert settings.provider_for("chat") == "ollama"
    assert settings.provider_for("judge") == "ollama"
    assert settings.model_for("chat") == "llama3.2"
    assert settings.model_for("judge") == "qwen2.5vl"
    assert settings.active_image_provider == "compositor"
    assert settings.missing_credentials() == []


def test_development_can_opt_into_a_hosted_role(env):
    settings = env(IMAGE_PROVIDER="openai", OPENAI_API_KEY="sk")
    assert settings.active_image_provider == "openai"
    assert settings.image_quality == "low"
    assert settings.bedrock_image_model_id == "stability.stable-image-core-v1:1"


def test_production_uses_hosted_models_and_high_quality(env):
    settings = env(APP_ENV="production", **HOSTED)
    assert settings.model_for("chat") == "gpt-4o-mini"
    assert settings.model_for("judge") == "gpt-4o-mini"
    assert settings.image_quality == "high"


def test_bedrock_judge_defaults_to_the_chat_model(env):
    settings = env(
        APP_ENV="production",
        CHAT_PROVIDER="bedrock",
        JUDGE_PROVIDER="bedrock",
        IMAGE_PROVIDER="bedrock",
        BEDROCK_CHAT_MODEL="claude",
    )
    assert settings.model_for("judge") == "claude"
    assert settings.bedrock_image_model_id == "stability.stable-image-ultra-v1:1"


@pytest.mark.parametrize(
    "overrides",
    [
        {"CHAT_PROVIDER": "ollama"},
        {"JUDGE_PROVIDER": "studio"},
        {"IMAGE_PROVIDER": "compositor"},
        {"OPENAI_API_KEY": ""},
        {"CHAT_PROVIDER": "bedrock"},
    ],
)
def test_production_refuses_to_start_without_hosted_providers(env, overrides):
    with pytest.raises(ValidationError):
        env(APP_ENV="production", **{**HOSTED, **overrides})
