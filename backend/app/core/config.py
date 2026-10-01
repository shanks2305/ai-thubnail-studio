from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

AppEnv = Literal["development", "production"]
TextProvider = Literal["ollama", "openai", "bedrock", "studio"]
ImageProvider = Literal["openai", "bedrock", "compositor"]
ImageQuality = Literal["low", "medium", "high"]

HOSTED_PROVIDERS = {"openai", "bedrock"}
BEDROCK_IMAGE_MODELS: dict[AppEnv, str] = {
    "development": "stability.stable-image-core-v1:1",
    "production": "stability.stable-image-ultra-v1:1",
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_ignore_empty=True)

    app_env: AppEnv = "development"
    text_provider: TextProvider | None = None
    image_provider: ImageProvider | None = None
    database_url: str = "sqlite:///./thumbnail_suite.db"
    storage_dir: str = "./storage"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_image_model: str = "gpt-image-2"
    openai_image_quality: ImageQuality | None = None
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    aws_region: str = "us-west-2"
    bedrock_text_model: str = ""
    bedrock_image_model: str = ""
    max_revisions: int = 2
    pass_score: int = 75
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @model_validator(mode="after")
    def _require_hosted_providers_in_production(self) -> "Settings":
        if self.app_env != "production":
            return self
        problems: list[str] = []
        if self.text_provider not in HOSTED_PROVIDERS:
            problems.append("TEXT_PROVIDER must be openai or bedrock in production.")
        if self.image_provider not in HOSTED_PROVIDERS:
            problems.append("IMAGE_PROVIDER must be openai or bedrock in production.")
        problems.extend(self.missing_credentials())
        if problems:
            raise ValueError(" ".join(problems))
        return self

    @property
    def active_text_provider(self) -> TextProvider:
        return self.text_provider or "ollama"

    @property
    def active_image_provider(self) -> ImageProvider:
        if self.image_provider:
            return self.image_provider
        return "openai" if self.openai_api_key else "compositor"

    @property
    def image_quality(self) -> ImageQuality:
        return self.openai_image_quality or ("high" if self.app_env == "production" else "low")

    @property
    def bedrock_image_model_id(self) -> str:
        return self.bedrock_image_model or BEDROCK_IMAGE_MODELS[self.app_env]

    def missing_credentials(self) -> list[str]:
        providers = {self.active_text_provider, self.active_image_provider}
        problems: list[str] = []
        if "openai" in providers and not self.openai_api_key:
            problems.append("Set OPENAI_API_KEY.")
        if self.active_text_provider == "bedrock" and not self.bedrock_text_model:
            problems.append("Set BEDROCK_TEXT_MODEL.")
        return problems

    @property
    def storage_path(self) -> Path:
        return Path(self.storage_dir).resolve()

    @property
    def origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
