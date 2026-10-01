import re
from urllib.parse import quote

import httpx

_API = "https://en.wikipedia.org/w/api.php"
_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/"
_AGENT = {"User-Agent": "ThumbnailSuite/0.1 (local thumbnail research)"}
_SKIP = {
    "i", "we", "my", "the", "a", "an", "how", "why", "what", "when", "this", "that",
    "playing", "played", "play", "streaming",
}
_PLAYING = re.compile(
    r"\b(?:[Pp]laying|[Pp]layed|[Ss]treaming|[Pp]lay)\s+([A-Z0-9][\w:'’\-]+(?:\s+[A-Z0-9][\w:'’\-]+){0,3})"
)
_GAMEPLAY = re.compile(
    r"\b([A-Z0-9][\w:'’\-]+(?:\s+[A-Z0-9][\w:'’\-]+){0,3})\s+(?:gameplay|highlights|ranked|clutch)\b"
)
_GAME_WORDS = ("video game", "esport", "multiplayer", "shooter", "battle royale", "mmorpg", "developed by")


def candidate_names(title: str, description: str) -> list[str]:
    text = f"{title}\n{description}"
    names = [*_PLAYING.findall(text), *_GAMEPLAY.findall(text)]
    head = re.split(r"[|\-–—]", title)[0].strip()
    words = head.split()
    if words and len(words) <= 6 and words[0].lower() not in _SKIP and words[0][:1].isupper():
        names.append(head)
    unique: list[str] = []
    for name in names:
        cleaned = " ".join(name.split())
        if cleaned and cleaned.lower() not in {item.lower() for item in unique} and _keep(cleaned):
            unique.append(cleaned)
    return unique[:4]


def lookup_game(title: str, description: str) -> dict[str, str] | None:
    for name in candidate_names(title, description):
        page = _wiki_game(name)
        if page is not None:
            return page
    return None


def is_game_page(text: str) -> bool:
    lowered = text.lower()
    return any(word in lowered for word in _GAME_WORDS)


def _wiki_game(name: str) -> dict[str, str] | None:
    try:
        found = httpx.get(
            _API,
            params={"action": "query", "list": "search", "srsearch": f"{name} video game", "srlimit": 1, "format": "json"},
            headers=_AGENT,
            timeout=8,
        )
        hits = found.json().get("query", {}).get("search", []) if found.status_code == 200 else []
        if not hits:
            return None
        page_title = str(hits[0].get("title") or "")
        summary = httpx.get(f"{_SUMMARY}{quote(page_title.replace(' ', '_'))}", headers=_AGENT, timeout=8)
    except (httpx.HTTPError, ValueError):
        return None
    if summary.status_code != 200:
        return None
    payload = summary.json()
    blurb = f"{payload.get('description') or ''}. {payload.get('extract') or ''}"
    if not is_game_page(blurb):
        return None
    source = ""
    urls = payload.get("content_urls")
    if isinstance(urls, dict):
        desktop = urls.get("desktop")
        if isinstance(desktop, dict):
            source = str(desktop.get("page") or "")
    return {"name": page_title[:120], "summary": str(payload.get("extract") or "")[:500], "source": source[:300]}


def _keep(name: str) -> bool:
    first = name.split()[0].lower()
    return first not in _SKIP and len(name) <= 60
