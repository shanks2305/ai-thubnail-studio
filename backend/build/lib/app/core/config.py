from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

AppEnv = Literal["development", "production"]
AgentRole = Literal["chat", "judge"]
# "studio" is the built-in engine: templated concepts for chat, pixel checks for the judge.
ModelProvider = Literal["ollama", "openai", "bedrock", "studio"]
ImageProvider = Literal["ollama", "openai", "bedrock", "compositor"]
ImageQuality = Literal["low", "medium", "high"]

HOSTED_PROVIDERS = {"openai", "bedrock"}
DEVELOPMENT_MODEL_PROVIDER: ModelProvider = "ollama"
DEVELOPMENT_IMAGE_PROVIDER: ImageProvider = "compositor"
BEDROCK_IMAGE_MODELS: dict[AppEnv, str] = {
    "development": "stability.stable-image-core-v1:1",
    "production": "stability.stable-image-ultra-v1:1",
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_ignore_empty=True)

    app_env: AppEnv = "development"
    chat_provider: ModelProvider | None = None
    judge_provider: ModelProvider | None = None
    image_provider: ImageProvider | None = None
    database_url: str = "sqlite:///./thumbnail_suite.db"
    storage_dir: str = "./storage"
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    openai_judge_model: str = "gpt-4o-mini"
    openai_image_model: str = "gpt-image-2"
    openai_image_quality: ImageQuality | None = None
    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "llama3.2"
    ollama_judge_model: str = "qwen2.5vl"
    ollama_image_model: str = "x/flux2-klein:4b"
    aws_region: str = "us-west-2"
    bedrock_chat_model: str = ""
    bedrock_judge_model: str = ""
    bedrock_image_model: str = ""
    max_revisions: int = 2
    pass_score: int = 75
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @model_validator(mode="after")
    def _require_hosted_providers_in_production(self) -> "Settings":
        if self.app_env != "production":
            return self
        problems = [
            f"{name} must be openai or bedrock in production."
            for name, value in (
                ("CHAT_PROVIDER", self.chat_provider),
                ("JUDGE_PROVIDER", self.judge_provider),
                ("IMAGE_PROVIDER", self.image_provider),
            )
            if value not in HOSTED_PROVIDERS
        ]
        problems.extend(self.missing_credentials())
        if problems:
            raise ValueError(" ".join(problems))
        return self

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    def provider_for(self, role: AgentRole) -> ModelProvider:
        chosen = self.chat_provider if role == "chat" else self.judge_provider
        return chosen or DEVELOPMENT_MODEL_PROVIDER

    def model_for(self, role: AgentRole) -> str:
        models: dict[ModelProvider, tuple[str, str]] = {
            "ollama": (self.ollama_chat_model, self.ollama_judge_model),
            "openai": (self.openai_chat_model, self.openai_judge_model),
            "bedrock": (self.bedrock_chat_model, self.bedrock_judge_model or self.bedrock_chat_model),
            "studio": ("local-studio", "pixel-critic"),
        }
        chat_model, judge_model = models[self.provider_for(role)]
        return chat_model if role == "chat" else judge_model

    @property
    def active_image_provider(self) -> ImageProvider:
        return self.image_provider or DEVELOPMENT_IMAGE_PROVIDER

    @property
    def image_quality(self) -> ImageQuality:
        return self.openai_image_quality or ("high" if self.is_production else "low")

    @property
    def bedrock_image_model_id(self) -> str:
        return self.bedrock_image_model or BEDROCK_IMAGE_MODELS[self.app_env]

    def missing_credentials(self) -> list[str]:
        providers = {self.provider_for("chat"), self.provider_for("judge"), self.active_image_provider}
        problems: list[str] = []
        if "openai" in providers and not self.openai_api_key:
            problems.append("Set OPENAI_API_KEY.")
        for role in ("chat", "judge"):
            if self.provider_for(role) == "bedrock" and not self.model_for(role):
                problems.append(f"Set BEDROCK_{role.upper()}_MODEL.")
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
