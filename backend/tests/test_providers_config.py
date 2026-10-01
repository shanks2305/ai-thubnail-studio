import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings
from app.providers.router import text_provider_for
from app.tools.image_generation import image_provider_for

PROVIDER_ENV = ("APP_ENV", "TEXT_PROVIDER", "IMAGE_PROVIDER", "OPENAI_API_KEY", "BEDROCK_TEXT_MODEL", "OPENAI_IMAGE_QUALITY")


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


def test_development_defaults_to_ollama_and_offline_images(env):
    settings = env()
    assert settings.active_text_provider == "ollama"
    assert settings.active_image_provider == "compositor"


def test_development_uses_cheap_openai_images_when_a_key_is_set(env):
    settings = env(OPENAI_API_KEY="sk")
    assert settings.active_image_provider == "openai"
    assert settings.image_quality == "low"
    assert settings.bedrock_image_model_id == "stability.stable-image-core-v1:1"


def test_production_uses_high_quality_defaults(env):
    settings = env(APP_ENV="production", TEXT_PROVIDER="bedrock", IMAGE_PROVIDER="bedrock", BEDROCK_TEXT_MODEL="m")
    assert settings.image_quality == "high"
    assert settings.bedrock_image_model_id == "stability.stable-image-ultra-v1:1"


@pytest.mark.parametrize(
    "values",
    [
        {"TEXT_PROVIDER": "ollama", "IMAGE_PROVIDER": "openai", "OPENAI_API_KEY": "sk"},
        {"TEXT_PROVIDER": "openai", "IMAGE_PROVIDER": "compositor", "OPENAI_API_KEY": "sk"},
        {"TEXT_PROVIDER": "openai", "IMAGE_PROVIDER": "openai"},
        {"TEXT_PROVIDER": "bedrock", "IMAGE_PROVIDER": "bedrock"},
    ],
)
def test_production_refuses_to_start_without_hosted_providers(env, values):
    with pytest.raises(ValidationError):
        env(APP_ENV="production", **values)


def test_local_projects_never_use_hosted_providers(env, monkeypatch):
    env(TEXT_PROVIDER="openai", IMAGE_PROVIDER="openai", OPENAI_API_KEY="sk")
    monkeypatch.setattr("app.providers.router.ollama_reachable", lambda: False)
    assert text_provider_for("local") == "studio"
    assert image_provider_for("local") == "compositor"
    assert text_provider_for("hybrid") == "openai"
    assert image_provider_for("cloud") == "openai"
