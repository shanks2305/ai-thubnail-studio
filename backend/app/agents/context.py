from sqlalchemy.orm import Session

from app.db.library import BrandKit, Channel, CreatorProfile
from app.db.models import Project
from app.domain.state import DesignSpec


def style_context(session: Session, project: Project) -> dict:
    payload: dict = {
        "creative_style": project.creative_style or "cinematic",
        "has_people": any(asset.kind in {"face", "person", "video_person"} for asset in project.assets),
    }
    if project.audience_brief:
        payload["audience_brief"] = project.audience_brief
    if project.brand_kit_id:
        kit = session.get(BrandKit, project.brand_kit_id)
        if kit is not None:
            payload["brand"] = {"name": kit.name, "colors": list(kit.colors or []), "font": kit.font}
    if project.creator_profile_id:
        profile = session.get(CreatorProfile, project.creator_profile_id)
        if profile is not None and profile.style_profile:
            payload["creator_style"] = profile.style_profile
    if project.channel_id:
        channel = session.get(Channel, project.channel_id)
        if channel is not None and channel.style_profile:
            payload["channel_style"] = channel.style_profile
    return payload


def apply_brand(spec: DesignSpec, context: dict) -> DesignSpec:
    brand = context.get("brand")
    if not isinstance(brand, dict):
        return spec
    colors = [str(color) for color in brand.get("colors") or [] if isinstance(color, str)]
    if colors:
        spec.palette = colors[:6]
    if brand.get("font") in {"anton", "bebas"}:
        spec.text.font = brand["font"]
    spec.text.stroke = True
    return spec
