import pytest
from PIL import Image

from app.agents import judge
from app.core.config import get_settings
from app.db.models import Project
from app.domain.state import Critique, DesignSpec, Issue, TextSpec
from app.providers.base import ProviderError
from app.tools.compositor import compose


@pytest.fixture
def configure(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    def apply(**values: str) -> None:
        defaults = {"APP_ENV": "development", "JUDGE_PROVIDER": "ollama", "PASS_SCORE": "75"}
        for key, value in {**defaults, **values}.items():
            monkeypatch.setenv(key, value)
        get_settings.cache_clear()

    yield apply
    get_settings.cache_clear()


@pytest.fixture
def calls(monkeypatch):
    recorded: dict[str, list] = {"model": [], "checks": []}
    monkeypatch.setattr(judge, "record_step", lambda *args: recorded["checks"].append(args))
    return recorded


def _spec() -> DesignSpec:
    return DesignSpec(text=TextSpec(content="AI WON", position="left", color="#ffffff"))


def _render(background: str) -> Image.Image:
    return compose(Image.new("RGB", (1280, 720), background), _spec())


def _judge_returns(monkeypatch, calls, verdict: Critique | Exception) -> None:
    def fake_run(session, project, task, payload, model, images=()):
        calls["model"].append({"task": task, "images": images})
        if isinstance(verdict, Exception):
            raise verdict
        return verdict

    monkeypatch.setattr(judge, "run_structured", fake_run)


def _project() -> Project:
    return Project(id="p1", title="t", description="A video about trains.")


def test_failed_pixel_checks_skip_the_judge_model(configure, calls, monkeypatch):
    configure()
    _judge_returns(monkeypatch, calls, Critique(overall=99, passed=True))
    critique = judge.judge_thumbnail(None, _project(), _render("white"), _spec())
    assert critique.passed is False
    assert calls["model"] == []
    assert len(calls["checks"]) == 1


def test_judge_model_sees_the_image_and_decides(configure, calls, monkeypatch):
    configure()
    verdict = Critique(overall=60, passed=True, issues=[Issue(type="clutter", severity="medium", message="Busy")])
    _judge_returns(monkeypatch, calls, verdict)
    critique = judge.judge_thumbnail(None, _project(), _render("black"), _spec())
    assert calls["model"][0]["task"] == "critic"
    assert calls["model"][0]["images"][0].startswith(b"\x89PNG")
    assert critique.overall == 60
    assert critique.passed is False  # below PASS_SCORE, whatever the model claimed


def test_studio_judge_uses_pixel_checks_only(configure, calls, monkeypatch):
    configure(JUDGE_PROVIDER="studio")
    _judge_returns(monkeypatch, calls, Critique(overall=10, passed=False))
    critique = judge.judge_thumbnail(None, _project(), _render("black"), _spec())
    assert critique.passed is True
    assert calls["model"] == []


def test_development_falls_back_to_pixel_checks_when_the_judge_fails(configure, calls, monkeypatch):
    configure()
    _judge_returns(monkeypatch, calls, ProviderError("down"))
    critique = judge.judge_thumbnail(None, _project(), _render("black"), _spec())
    assert critique.passed is True
    assert len(calls["checks"]) == 1


def test_production_reports_judge_failures(configure, calls, monkeypatch):
    configure(
        APP_ENV="production",
        CHAT_PROVIDER="openai",
        JUDGE_PROVIDER="openai",
        IMAGE_PROVIDER="openai",
        OPENAI_API_KEY="sk",
    )
    _judge_returns(monkeypatch, calls, ProviderError("down"))
    with pytest.raises(ProviderError):
        judge.judge_thumbnail(None, _project(), _render("black"), _spec())
