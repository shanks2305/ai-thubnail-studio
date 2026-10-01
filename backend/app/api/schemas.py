from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.tools.youtube import parse_video_id


class CreateProjectBody(BaseModel):
    description: str = Field(min_length=8, max_length=5000)
    youtube_url: str | None = None
    privacy_mode: Literal["local", "hybrid", "cloud"] = "hybrid"

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


class TextUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=80)
    position: Literal["left", "center", "right"]
    size: Literal["medium", "large", "very large"]
    color: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")


def title_from_description(description: str) -> str:
    text = " ".join(description.split())
    for mark in ".?!":
        if mark in text:
            text = text.split(mark)[0]
            break
    return text[:180] or "Untitled project"
