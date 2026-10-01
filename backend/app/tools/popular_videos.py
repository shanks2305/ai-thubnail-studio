from urllib.parse import urlparse

import httpx

_SEARCH = "https://www.googleapis.com/youtube/v3/search"
_VIDEOS = "https://www.googleapis.com/youtube/v3/videos"
_HOSTS = {"i.ytimg.com", "i9.ytimg.com", "yt3.ggpht.com"}
_LIMIT = 4


def is_live_url(url: str) -> bool:
    return "/live/" in urlparse(url).path


def search_query(game: str, title: str, live: bool) -> str:
    subject = game.strip() or title.strip()
    if not subject:
        return ""
    if live:
        return f"{subject} live"
    if game.strip():
        return f"{game.strip()} gameplay"
    return subject


def fetch_popular(query: str, exclude_id: str, api_key: str) -> list[dict]:
    if not api_key or not query.strip():
        return []
    try:
        found = httpx.get(
            _SEARCH,
            params={"part": "snippet", "type": "video", "q": query, "maxResults": 8, "key": api_key},
            timeout=8,
        )
        if found.status_code != 200:
            return []
        ids = [
            str((item.get("id") or {}).get("videoId") or "")
            for item in found.json().get("items", [])
            if (item.get("id") or {}).get("videoId") not in {None, "", exclude_id}
        ]
        if not ids:
            return []
        details = httpx.get(
            _VIDEOS,
            params={"part": "snippet,statistics", "id": ",".join(ids[:8]), "key": api_key},
            timeout=8,
        )
    except (httpx.HTTPError, ValueError):
        return []
    if details.status_code != 200:
        return []
    return videos_from_api(details.json(), exclude_id)


def videos_from_api(payload: dict, exclude_id: str) -> list[dict]:
    rows = []
    for item in payload.get("items", []):
        video_id = str(item.get("id") or "")
        snippet = item.get("snippet") if isinstance(item.get("snippet"), dict) else {}
        thumbnail = _thumbnail(snippet)
        if not video_id or video_id == exclude_id or not thumbnail or not snippet.get("title"):
            continue
        stats = item.get("statistics") if isinstance(item.get("statistics"), dict) else {}
        try:
            views = int(stats.get("viewCount") or 0)
        except (TypeError, ValueError):
            views = 0
        rows.append(
            {
                "title": str(snippet["title"])[:200],
                "views": views,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail_url": thumbnail,
            }
        )
    rows.sort(key=lambda row: int(row["views"]), reverse=True)
    return rows[:_LIMIT]


def _thumbnail(snippet: dict) -> str:
    thumbs = snippet.get("thumbnails") if isinstance(snippet.get("thumbnails"), dict) else {}
    for key in ("maxres", "high", "medium", "default"):
        url = str((thumbs.get(key) or {}).get("url") or "")
        host = urlparse(url).netloc.lower()
        if url.startswith("https://") and host in _HOSTS:
            return url
    return ""
