from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./thumbnail_suite.db"
    storage_dir: str = "./storage"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_image_model: str = "dall-e-3"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    llm_mode: str = "auto"
    max_revisions: int = 2
    pass_score: int = 75
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def storage_path(self) -> Path:
        return Path(self.storage_dir).resolve()

    @property
    def origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
