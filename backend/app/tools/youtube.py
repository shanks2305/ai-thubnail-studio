from io import BytesIO
from urllib.parse import parse_qs, urlparse

import httpx
from PIL import Image
from pydantic import BaseModel

YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "www.youtu.be"}


class YoutubeMetadata(BaseModel):
    video_id: str
    title: str
    author: str
    thumbnail_url: str


def parse_video_id(url: str) -> str | None:
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower()
    if host not in YOUTUBE_HOSTS:
        return None
    if host.endswith("youtu.be"):
        video_id = parsed.path.strip("/").split("/")[0]
        return video_id or None
    if parsed.path == "/watch":
        return parse_qs(parsed.query).get("v", [None])[0]
    parts = [part for part in parsed.path.split("/") if part]
    if parts and parts[0] in {"shorts", "embed", "live"} and len(parts) > 1:
        return parts[1]
    return None


def fetch_youtube(url: str) -> YoutubeMetadata | None:
    video_id = parse_video_id(url)
    if video_id is None:
        return None
    watch = f"https://www.youtube.com/watch?v={video_id}"
    try:
        response = httpx.get(
            "https://www.youtube.com/oembed",
            params={"url": watch, "format": "json"},
            timeout=8,
        )
    except httpx.HTTPError:
        return None
    if response.status_code != 200:
        return None
    payload = response.json()
    title = str(payload.get("title") or "").strip()
    if not title:
        return None
    return YoutubeMetadata(
        video_id=video_id,
        title=title[:300],
        author=str(payload.get("author_name") or "")[:200],
        thumbnail_url=str(payload.get("thumbnail_url") or ""),
    )


def video_still_bytes(video_id: str, fallback_url: str) -> bytes | None:
    urls = [
        f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
        f"https://i.ytimg.com/vi/{video_id}/sddefault.jpg",
        f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
        fallback_url,
    ]
    for url in urls:
        data = download_bytes(url)
        if data is None:
            continue
        try:
            image = Image.open(BytesIO(data))
        except OSError:
            continue
        if image.width >= 320:
            return data
    return None


def download_bytes(url: str) -> bytes | None:
    if not url.startswith("https://"):
        return None
    try:
        response = httpx.get(url, timeout=8, follow_redirects=True)
    except httpx.HTTPError:
        return None
    content_type = response.headers.get("content-type", "")
    if response.status_code != 200 or not content_type.startswith("image/"):
        return None
    return response.content
