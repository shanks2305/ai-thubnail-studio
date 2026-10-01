import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'app.db'}")
    monkeypatch.setenv("STORAGE_DIR", str(tmp_path / "storage"))
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("TEXT_PROVIDER", "studio")
    monkeypatch.setenv("IMAGE_PROVIDER", "compositor")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    from app.core.config import get_settings
    from app.core.database import reset_engine
    from app.providers.ollama import reset_ollama_cache
    from app.services.events import bus

    get_settings.cache_clear()
    reset_engine()
    reset_ollama_cache()
    bus.clear()
    from app.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client
