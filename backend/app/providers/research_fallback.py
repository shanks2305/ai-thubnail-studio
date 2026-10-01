from typing import Any


def research_from_gathered(payload: dict[str, Any]) -> dict[str, Any]:
    gathered = payload.get("gathered") if isinstance(payload.get("gathered"), dict) else {}
    game = _game(gathered.get("game"))
    popular = _popular(gathered.get("popular_videos"))
    blocked = ["Do not invent scores, ranks, patch notes, or people who were not named."]
    if game is None:
        blocked.append("No game page was found. Do not name a game.")
    if not _strings(gathered.get("names")):
        blocked.append("Do not name a player or creator.")
    return {
        "game": game,
        "facts": _strings(gathered.get("facts")),
        "names": _strings(gathered.get("names")),
        "numbers": _strings(gathered.get("numbers")),
        "visual_anchor": str(gathered.get("visual_anchor") or "")[:240],
        "do_not_invent": blocked,
        "face_count": _count(gathered.get("face_count")),
        "popular_videos": popular,
    }


def _game(value: object) -> dict[str, str] | None:
    if not isinstance(value, dict) or not str(value.get("name") or "").strip():
        return None
    return {
        "name": str(value["name"])[:120],
        "summary": str(value.get("summary") or "")[:500],
        "source": str(value.get("source") or "")[:300],
    }


def _popular(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    rows = []
    for item in value:
        if not isinstance(item, dict) or not str(item.get("title") or "").strip():
            continue
        rows.append(
            {"title": str(item["title"])[:200], "views": _count(item.get("views")), "url": str(item.get("url") or "")[:300]}
        )
    return rows[:4]


def _strings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()][:8]


def _count(value: object) -> int:
    try:
        return max(0, int(value))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0
