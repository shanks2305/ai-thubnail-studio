from pydantic import Field, field_validator, model_validator

from app.domain.state import _Model


class GameProfile(_Model):
    name: str
    summary: str = ""
    source: str = ""


class PopularVideo(_Model):
    title: str
    views: int = 0
    url: str = ""

    @field_validator("views", mode="before")
    @classmethod
    def _views(cls, value: object) -> int:
        try:
            return max(0, int(value))  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return 0


class ResearchBrief(_Model):
    game: GameProfile | None = None
    facts: list[str] = Field(default_factory=list)
    names: list[str] = Field(default_factory=list)
    numbers: list[str] = Field(default_factory=list)
    visual_anchor: str = ""
    do_not_invent: list[str] = Field(default_factory=list)
    face_count: int = 0
    popular_videos: list[PopularVideo] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _shape(cls, value: object) -> object:
        if not isinstance(value, dict):
            return value
        data = dict(value)
        game = data.get("game")
        if isinstance(game, str) and game.strip():
            data["game"] = {"name": game.strip(), "summary": ""}
        elif not isinstance(game, dict) or not str(game.get("name") or "").strip():
            data["game"] = None
        for key in ("facts", "names", "numbers", "do_not_invent"):
            data[key] = _strings(data.get(key))
        data["popular_videos"] = _videos(data.get("popular_videos"))
        data["face_count"] = _count(data.get("face_count"))
        return data


def _strings(value: object) -> list[str]:
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()][:8]


def _videos(value: object) -> list[object]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict) and str(item.get("title") or "").strip()][:4]


def _count(value: object) -> int:
    try:
        return max(0, int(value))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0
