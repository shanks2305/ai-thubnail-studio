from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    youtube_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    youtube_title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    owner_id: Mapped[str] = mapped_column(String(64), default="local")
    status: Mapped[str] = mapped_column(String(32), default="draft")
    favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    video_brief: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    reference_profile: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    hooks: Mapped[list | None] = mapped_column(JSON, nullable=True)
    selected_concept_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    selected_generation_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    brand_kit_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    creator_profile_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    channel_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    creative_style: Mapped[str] = mapped_column(String(32), default="cinematic")
    audience_brief: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    shared: Mapped[bool] = mapped_column(Boolean, default=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    assets: Mapped[list["Asset"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    concepts: Mapped[list["Concept"]] = relationship(
        back_populates="project", cascade="all, delete-orphan", order_by="Concept.position"
    )
    generations: Mapped[list["Generation"]] = relationship(
        back_populates="project", cascade="all, delete-orphan", order_by="Generation.created_at"
    )
    agent_runs: Mapped[list["AgentRun"]] = relationship(
        back_populates="project", cascade="all, delete-orphan", order_by="AgentRun.started_at"
    )


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(32))
    content_type: Mapped[str] = mapped_column(String(100))
    path: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    project: Mapped[Project] = relationship(back_populates="assets")


class Concept(Base):
    __tablename__ = "concepts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(160))
    hook: Mapped[str] = mapped_column(String(200))
    visual_story: Mapped[str] = mapped_column(Text)
    subject: Mapped[str] = mapped_column(Text)
    background: Mapped[str] = mapped_column(Text)
    composition: Mapped[str] = mapped_column(Text)
    text: Mapped[str] = mapped_column(String(200))
    emotional_direction: Mapped[str] = mapped_column(String(200))
    why_it_works: Mapped[str] = mapped_column(Text)
    image_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
    project: Mapped[Project] = relationship(back_populates="concepts")


class Generation(Base):
    __tablename__ = "generations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    concept_id: Mapped[str] = mapped_column(ForeignKey("concepts.id", ondelete="CASCADE"))
    attempt: Mapped[int] = mapped_column(Integer, default=1)
    variation_axis: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source_generation_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="completed")
    design_spec: Mapped[dict] = mapped_column(JSON)
    background_asset_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    image_asset_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    project: Mapped[Project] = relationship(back_populates="generations")
    critique: Mapped["CritiqueRow | None"] = relationship(
        back_populates="generation", cascade="all, delete-orphan", uselist=False
    )


class CritiqueRow(Base):
    __tablename__ = "critiques"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    generation_id: Mapped[str] = mapped_column(ForeignKey("generations.id", ondelete="CASCADE"), unique=True)
    overall: Mapped[int] = mapped_column(Integer)
    passed: Mapped[bool] = mapped_column(Boolean)
    issues: Mapped[list] = mapped_column(JSON)
    recommended_changes: Mapped[list] = mapped_column(JSON)
    generation: Mapped[Generation] = relationship(back_populates="critique")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    agent: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32))
    provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    output: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    project: Mapped[Project] = relationship(back_populates="agent_runs")
