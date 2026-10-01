from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class _Model(BaseModel):
    model_config = ConfigDict(extra="ignore")


class VideoBrief(_Model):
    topic: str
    core_story: str
    central_tension: str
    key_entities: list[str] = Field(default_factory=list)
    audience: str
    emotional_angles: list[str] = Field(default_factory=list)
    visual_opportunities: list[str] = Field(default_factory=list)


class ReferenceProfile(_Model):
    style_summary: str
    composition: dict[str, Any] = Field(default_factory=dict)
    typography: dict[str, Any] = Field(default_factory=dict)
    color_palette: list[str] = Field(default_factory=list)
    visual_language: list[str] = Field(default_factory=list)
    do_not_copy: list[str] = Field(default_factory=list)

    @field_validator("color_palette", mode="before")
    @classmethod
    def _colors(cls, value: object) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item) for item in value][:6]


class Hook(_Model):
    id: str = ""
    text: str
    angle: str


class HookList(_Model):
    hooks: list[Hook]


class ThumbnailConcept(_Model):
    id: str = ""
    name: str
    hook: str
    visual_story: str
    subject: str
    background: str
    composition: str
    text: str
    emotional_direction: str
    why_it_works: str


class ConceptList(_Model):
    concepts: list[ThumbnailConcept]


class TextSpec(_Model):
    content: str
    position: Literal["left", "center", "right"] = "left"
    size: Literal["medium", "large", "very large"] = "very large"
    color: str = "#ffffff"
    font: Literal["anton", "bebas"] = "anton"
    stroke: bool = False
    vertical: Literal["top", "middle", "bottom"] = "middle"


class DesignSpec(_Model):
    canvas: str = "1280x720"
    subject: dict[str, Any] = Field(default_factory=dict)
    background: dict[str, Any] = Field(default_factory=dict)
    lighting: str = ""
    composition: str = ""
    text: TextSpec
    image_prompt: str = ""
    palette: list[str] = Field(default_factory=list)
    scrim: bool = False
    scrim_strength: float = 0
    recolor: bool = False

    @field_validator("scrim_strength", mode="before")
    @classmethod
    def _strength(cls, value: object) -> float:
        try:
            number = float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return 0
        return min(1.0, max(0.0, number))

    @field_validator("palette", mode="before")
    @classmethod
    def _palette(cls, value: object) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item) for item in value][:6]


class AudienceBrief(_Model):
    viewer: str
    belief: str
    click_reason: str
    avoid: list[str] = Field(default_factory=list)


class Issue(_Model):
    type: str
    severity: Literal["low", "medium", "high"]
    message: str


class Critique(_Model):
    overall: int
    issues: list[Issue] = Field(default_factory=list)
    recommended_changes: list[str] = Field(default_factory=list)
    passed: bool
