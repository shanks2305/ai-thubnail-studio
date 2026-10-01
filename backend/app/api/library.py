import re

from pydantic import BaseModel, Field, field_validator


class BrandBody(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    colors: list[str] = Field(min_length=1, max_length=3)
    font: str = "anton"
    shared: bool = False

    @field_validator("colors")
    @classmethod
    def hex_colors(cls, value: list[str]) -> list[str]:
        cleaned = []
        for item in value:
            if re.fullmatch(r"#[0-9a-fA-F]{6}", item) is None:
                raise ValueError("Use hex colors like #112233.")
            cleaned.append(item.lower())
        return cleaned

    @field_validator("font")
    @classmethod
    def known_font(cls, value: str) -> str:
        if value not in {"anton", "bebas"}:
            raise ValueError("Font must be anton or bebas.")
        return value


class NamedBody(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    notes: str = ""
    shared: bool = False


class LearnBody(BaseModel):
    project_id: str


class ExperimentBody(BaseModel):
    generation_a_id: str
    generation_b_id: str


class ExperimentUpdate(BaseModel):
    winner_id: str | None = None
    notes: str | None = Field(default=None, max_length=500)


def visible_to_owner(row) -> bool:
    from app.api.access import current_owner

    return row.owner_id == current_owner() or bool(getattr(row, "shared", False))
