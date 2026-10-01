import re
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Asset, Project
from app.domain.state import VideoBrief
from app.tools import popular_videos, youtube
from app.tools.faces import save_player_faces
from app.tools.game_lookup import lookup_game
from app.tools.storage import delete_file, save_bytes
from app.tools.youtube import parse_video_id


def merge_research(parsed: dict, gathered: dict) -> dict:
    merged = dict(parsed)
    if gathered.get("game"):
        merged["game"] = gathered["game"]
    for key in ("names", "numbers", "popular_videos", "facts"):
        if gathered.get(key):
            merged[key] = gathered[key]
    if not str(merged.get("visual_anchor") or "").strip():
        merged["visual_anchor"] = str(gathered.get("visual_anchor") or "")
    merged["face_count"] = int(gathered.get("face_count") or 0)
    return merged


def gather_research(session: Session, project: Project, brief: VideoBrief, author: str = "") -> dict:
    title = project.youtube_title or project.title
    game = lookup_game(title, project.description)
    face_count = save_player_faces(session, project)
    live = popular_videos.is_live_url(project.youtube_url or "")
    query = popular_videos.search_query(str(game["name"]) if game else "", project.youtube_title or brief.topic, live)
    popular = _store_popular(session, project, query)
    facts: list[str] = []
    if face_count:
        facts.append(f"{face_count} photos of people in the video.")
    if popular:
        kind = "live streams" if live else "videos"
        facts.append(f"{len(popular)} popular {kind} about the same subject.")
    if game and game.get("summary"):
        anchor = f"{game['name']}: {str(game['summary']).split('.')[0]}"[:240]
    elif brief.visual_opportunities:
        anchor = brief.visual_opportunities[0][:240]
    else:
        anchor = ""
    names = [author.strip()] if author.strip() else []
    return {
        "game": game,
        "facts": facts,
        "names": names,
        "numbers": re.findall(r"\b\d+\b", project.description)[:4],
        "visual_anchor": anchor,
        "face_count": face_count,
        "popular_videos": popular,
    }


def _store_popular(session: Session, project: Project, query: str) -> list[dict]:
    video_id = parse_video_id(project.youtube_url or "") or ""
    rows = popular_videos.fetch_popular(query, video_id, get_settings().youtube_api_key)
    if not rows:
        return []
    for asset in list(project.assets):
        if asset.kind != "popular":
            continue
        delete_file(asset.path)
        session.delete(asset)
    session.flush()
    stored: list[dict] = []
    for row in rows:
        data = youtube.download_bytes(str(row["thumbnail_url"]))
        if data is None:
            continue
        path = save_bytes(project.id, "popular", data, ".jpg")
        session.add(Asset(id=str(uuid4()), project_id=project.id, kind="popular", content_type="image/jpeg", path=path))
        stored.append({"title": row["title"], "views": row["views"], "url": row["url"]})
    if stored:
        session.commit()
        session.refresh(project)
    return stored
