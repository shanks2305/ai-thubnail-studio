from typing import Literal

import re

from pydantic import BaseModel, Field, field_validator

from app.domain.styles import STYLE_IDS
from app.tools.youtube import parse_video_id


class CreateProjectBody(BaseModel):
    description: str = Field(min_length=8, max_length=5000)
    youtube_url: str | None = None
    brand_kit_id: str | None = None
    creator_profile_id: str | None = None
    channel_id: str | None = None
    creative_style: str = "cinematic"
    shared: bool = False

    @field_validator("creative_style")
    @classmethod
    def known_style(cls, value: str) -> str:
        if value not in STYLE_IDS:
            raise ValueError("Choose a creative style.")
        return value

    @field_validator("youtube_url")
    @classmethod
    def youtube(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        if parse_video_id(value) is None:
            raise ValueError("Enter a YouTube video URL.")
        return value.strip()


class UpdateProjectBody(BaseModel):
    favorite: bool | None = None
    shared: bool | None = None
    creative_style: str | None = None

    @field_validator("creative_style")
    @classmethod
    def known_style(cls, value: str | None) -> str | None:
        if value is not None and value not in STYLE_IDS:
            raise ValueError("Choose a creative style.")
        return value


class TextUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=80)
    position: Literal["left", "center", "right"]
    size: Literal["medium", "large", "very large"]
    color: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    font: Literal["anton", "bebas"] | None = None
    stroke: bool | None = None
    vertical: Literal["top", "middle", "bottom"] | None = None
    scrim_strength: float | None = Field(default=None, ge=0, le=1)
    palette: list[str] | None = None
    recolor: bool | None = None

    @field_validator("palette")
    @classmethod
    def palette_colors(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        cleaned: list[str] = []
        for item in value[:6]:
            if re.fullmatch(r"#[0-9a-fA-F]{6}", item) is None:
                raise ValueError("Colors must be hex values like #112233.")
            cleaned.append(item)
        return cleaned


class GenerateThumbnailBody(BaseModel):
    image_prompt: str | None = Field(default=None, max_length=3900)


class ConceptPrompt(BaseModel):
    image_prompt: str = Field(max_length=3900)


class VariationBody(BaseModel):
    axis: Literal["hook", "crop", "palette", "expression"]


class RerenderBody(BaseModel):
    instruction: str = Field(default="", max_length=500)


class PerformanceBody(BaseModel):
    impressions: int = Field(ge=0, le=1_000_000_000)
    clicks: int = Field(ge=0, le=1_000_000_000)


def title_from_description(description: str) -> str:
    text = " ".join(description.split())
    for mark in ".?!":
        if mark in text:
            text = text.split(mark)[0]
            break
    return text[:180] or "Untitled project"
