from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from app.api.access import current_owner, new_member_token
from app.api.library import BrandBody, ExperimentBody, ExperimentUpdate, LearnBody, NamedBody, visible_to_owner
from app.api.media import read_upload
from app.api.projects import require_project
from app.core.config import get_settings
from app.core.database import session_scope
from app.db.library import BrandKit, Channel, CreatorProfile, Experiment, Member
from app.db.models import Project, utcnow
from app.tools.storage import read_bytes, save_bytes

router = APIRouter()


@router.get("/brand-kits")
def list_brand_kits() -> list[dict]:
    with session_scope() as session:
        rows = session.query(BrandKit).order_by(BrandKit.created_at.desc()).all()
        return [_brand(row) for row in rows if visible_to_owner(row)]


@router.post("/brand-kits", status_code=201)
def create_brand_kit(body: BrandBody) -> dict:
    kit = BrandKit(
        id=str(uuid4()),
        owner_id=current_owner(),
        name=body.name.strip(),
        colors=body.colors,
        font=body.font,
        shared=body.shared,
    )
    with session_scope() as session:
        session.add(kit)
        session.flush()
        return _brand(kit)


@router.post("/brand-kits/{kit_id}/logo", status_code=201)
def upload_logo(kit_id: str, file: UploadFile = File(...)) -> dict:
    data, suffix, _content_type = read_upload(file)
    with session_scope() as session:
        kit = _require_kit(session, kit_id)
        kit.logo_path = save_bytes(kit.id, "logo", data, suffix)
        session.flush()
        return _brand(kit)


@router.get("/brand-kits/{kit_id}/logo")
def get_logo(kit_id: str) -> Response:
    with session_scope() as session:
        kit = _require_kit(session, kit_id)
        if not kit.logo_path:
            raise HTTPException(status_code=404, detail="This brand kit has no logo.")
        data = read_bytes(kit.logo_path)
        media_type = "image/jpeg" if kit.logo_path.endswith(".jpg") else "image/webp" if kit.logo_path.endswith(".webp") else "image/png"
    return Response(content=data, media_type=media_type)


@router.get("/profiles")
def list_profiles() -> list[dict]:
    with session_scope() as session:
        rows = session.query(CreatorProfile).order_by(CreatorProfile.created_at.desc()).all()
        return [_profile(row) for row in rows if visible_to_owner(row)]


@router.post("/projects/{project_id}/profile", status_code=201)
def save_profile(project_id: str, body: NamedBody) -> dict:
    with session_scope() as session:
        project = require_project(session, project_id)
        if not project.reference_profile:
            raise HTTPException(status_code=400, detail="Generate concepts before saving a style.")
        profile = CreatorProfile(
            id=str(uuid4()),
            owner_id=current_owner(),
            name=body.name.strip(),
            notes=body.notes.strip(),
            style_profile=project.reference_profile,
            shared=body.shared,
        )
        session.add(profile)
        project.creator_profile_id = profile.id
        project.updated_at = utcnow()
        session.flush()
        return _profile(profile)


@router.get("/channels")
def list_channels() -> list[dict]:
    owner = current_owner()
    with session_scope() as session:
        rows = session.query(Channel).filter_by(owner_id=owner).order_by(Channel.created_at.desc()).all()
        return [_channel(row) for row in rows]


@router.post("/channels", status_code=201)
def create_channel(body: NamedBody) -> dict:
    channel = Channel(id=str(uuid4()), owner_id=current_owner(), name=body.name.strip())
    with session_scope() as session:
        session.add(channel)
        session.flush()
        return _channel(channel)


@router.get("/channels/{channel_id}")
def read_channel(channel_id: str) -> dict:
    with session_scope() as session:
        channel = _require_channel(session, channel_id)
        projects = session.query(Project).filter_by(channel_id=channel.id).all()
        history = [_scored(project, generation) for project in projects for generation in project.generations]
        return {**_channel(channel), "thumbnails": [item for item in history if item]}


@router.post("/channels/{channel_id}/learn")
def learn_channel(channel_id: str, body: LearnBody) -> dict:
    with session_scope() as session:
        channel = _require_channel(session, channel_id)
        project = require_project(session, body.project_id)
        if not project.reference_profile:
            raise HTTPException(status_code=400, detail="Generate concepts before teaching a channel.")
        channel.style_profile = project.reference_profile
        project.channel_id = channel.id
        return _channel(channel)


@router.post("/projects/{project_id}/experiments", status_code=201)
def create_experiment(project_id: str, body: ExperimentBody) -> dict:
    with session_scope() as session:
        project = require_project(session, project_id)
        _require_generation(session, project.id, body.generation_a_id)
        _require_generation(session, project.id, body.generation_b_id)
        experiment = Experiment(
            id=str(uuid4()),
            project_id=project.id,
            generation_a_id=body.generation_a_id,
            generation_b_id=body.generation_b_id,
        )
        session.add(experiment)
        session.flush()
        return _experiment(experiment)


@router.patch("/experiments/{experiment_id}")
def update_experiment(experiment_id: str, body: ExperimentUpdate) -> dict:
    with session_scope() as session:
        experiment = session.get(Experiment, experiment_id)
        if experiment is None:
            raise HTTPException(status_code=404, detail="Experiment not found.")
        require_project(session, experiment.project_id)
        if body.winner_id is not None:
            if body.winner_id not in {experiment.generation_a_id, experiment.generation_b_id}:
                raise HTTPException(status_code=400, detail="The winner has to be one of the two thumbnails.")
            experiment.winner_id = body.winner_id
        if body.notes is not None:
            experiment.notes = body.notes.strip()
        session.flush()
        return _experiment(experiment)


@router.get("/team/members")
def list_members() -> list[dict]:
    if not get_settings().auth_token:
        return []
    with session_scope() as session:
        rows = session.query(Member).order_by(Member.created_at).all()
        return [{"id": row.id, "name": row.name} for row in rows]


@router.post("/team/members", status_code=201)
def add_member(body: NamedBody) -> dict:
    if not get_settings().auth_token:
        raise HTTPException(status_code=400, detail="Set AUTH_TOKEN before adding teammates.")
    token, digest = new_member_token()
    member = Member(id=str(uuid4()), name=body.name.strip(), token_hash=digest)
    with session_scope() as session:
        session.add(member)
        session.flush()
        return {"id": member.id, "name": member.name, "token": token}


def _require_kit(session, kit_id: str) -> BrandKit:
    kit = session.get(BrandKit, kit_id)
    if kit is None or not visible_to_owner(kit):
        raise HTTPException(status_code=404, detail="Brand kit not found.")
    return kit


def _require_channel(session, channel_id: str) -> Channel:
    channel = session.get(Channel, channel_id)
    if channel is None or channel.owner_id != current_owner():
        raise HTTPException(status_code=404, detail="Channel not found.")
    return channel


def _require_generation(session, project_id: str, generation_id: str) -> None:
    from app.db.models import Generation

    generation = session.get(Generation, generation_id)
    if generation is None or generation.project_id != project_id:
        raise HTTPException(status_code=404, detail="Thumbnail not found.")


def _brand(kit: BrandKit) -> dict:
    return {
        "id": kit.id,
        "name": kit.name,
        "colors": kit.colors,
        "font": kit.font,
        "shared": kit.shared,
        "logo_url": f"/api/brand-kits/{kit.id}/logo" if kit.logo_path else None,
    }


def _profile(profile: CreatorProfile) -> dict:
    return {"id": profile.id, "name": profile.name, "notes": profile.notes, "shared": profile.shared}


def _channel(channel: Channel) -> dict:
    return {"id": channel.id, "name": channel.name, "style_profile": channel.style_profile}


def _experiment(experiment: Experiment) -> dict:
    return {
        "id": experiment.id,
        "generation_a_id": experiment.generation_a_id,
        "generation_b_id": experiment.generation_b_id,
        "winner_id": experiment.winner_id,
        "notes": experiment.notes,
    }


def _scored(project: Project, generation) -> dict | None:
    if generation.critique is None:
        return None
    return {
        "project_id": project.id,
        "project_title": project.title,
        "generation_id": generation.id,
        "score": generation.critique.overall,
        "impressions": generation.impressions,
        "clicks": generation.clicks,
        "image_url": f"/api/assets/{generation.image_asset_id}" if generation.image_asset_id else None,
    }
