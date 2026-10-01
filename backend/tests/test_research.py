from io import BytesIO

from PIL import Image

from app.providers.research_fallback import research_from_gathered
from app.tools.faces import face_crop
from app.tools.game_lookup import candidate_names, is_game_page
from app.tools.popular_videos import is_live_url, search_query, videos_from_api
from app.tools.youtube import YoutubeMetadata


def test_face_crop_keeps_a_skin_region_and_skips_a_blue_frame():
    frame = Image.new("RGB", (640, 360), (20, 40, 80))
    assert face_crop(frame) is None
    for x in range(80, 180):
        for y in range(40, 180):
            frame.putpixel((x, y), (234, 192, 157))
    crop = face_crop(frame)
    assert crop is not None
    assert crop.size[0] < frame.size[0]


def test_candidate_names_find_the_game_and_skip_a_sentence():
    assert "Valorant" in candidate_names("Playing Valorant until Radiant", "")
    assert candidate_names("I tested 20 AI coding tools.", "Nothing about a title.") == []


def test_game_page_requires_game_language():
    assert is_game_page("2020 video game by Riot Games")
    assert not is_game_page("studio album by a band")


def test_search_query_uses_the_game_and_live_streams():
    assert search_query("Valorant", "ranked grind", False) == "Valorant gameplay"
    assert search_query("", "ranked grind", False) == "ranked grind"
    assert is_live_url("https://www.youtube.com/live/abcdefghijk")
    assert search_query("Valorant", "ranked grind", True) == "Valorant live"


def test_popular_videos_rank_by_views_and_skip_the_source():
    payload = {
        "items": [
            _video("aaa", "Small", 10),
            _video("bbb", "Huge", 90),
            _video("self", "Source", 500),
            _video("ccc", "Offsite", 80, thumbnail="https://example.com/a.jpg"),
        ]
    }
    ranked = videos_from_api(payload, "self")
    assert [row["title"] for row in ranked] == ["Huge", "Small"]
    assert ranked[0]["url"] == "https://www.youtube.com/watch?v=bbb"


def test_fallback_does_not_invent_a_game():
    brief = research_from_gathered({"gathered": {"facts": ["A quiet match."], "visual_anchor": "The scoreboard"}})
    assert brief["game"] is None
    assert any("Do not name a game." in item for item in brief["do_not_invent"])
    assert brief["visual_anchor"] == "The scoreboard"


def test_researcher_stores_faces_game_and_popular_thumbnails(client, monkeypatch):
    image = _jpeg()
    monkeypatch.setattr("app.agents.concept_pipeline.fetch_youtube", lambda url: _metadata())
    monkeypatch.setattr("app.agents.concept_pipeline.download_bytes", lambda url: image)
    monkeypatch.setattr("app.tools.youtube.download_bytes", lambda url: image)
    monkeypatch.setattr(
        "app.agents.research.lookup_game",
        lambda title, description: {"name": "Valorant", "summary": "Valorant is a video game.", "source": "https://en.wikipedia.org/wiki/Valorant"},
    )
    seen: dict[str, str] = {}

    def popular(query: str, exclude_id: str, api_key: str) -> list[dict]:
        seen["query"] = query
        seen["exclude"] = exclude_id
        return [{"title": "Radiant grind", "views": 1_500_000, "url": "https://www.youtube.com/watch?v=zzzzzzzzzzz", "thumbnail_url": "https://i.ytimg.com/vi/zzzzzzzzzzz/hqdefault.jpg"}]

    monkeypatch.setattr("app.tools.popular_videos.fetch_popular", popular)
    created = client.post(
        "/api/projects",
        json={"description": "Playing Valorant until Radiant after 40 games.", "youtube_url": "https://www.youtube.com/watch?v=abcdefghijk"},
    )
    project_id = created.json()["id"]
    assert client.post(f"/api/projects/{project_id}/generate").status_code == 202
    detail = client.get(f"/api/projects/{project_id}").json()
    assert any(run["agent"] == "researcher" and run["status"] == "completed" for run in detail["agent_runs"])
    assert detail["research_brief"]["game"]["name"] == "Valorant"
    assert detail["research_brief"]["face_count"] >= 1
    assert detail["research_brief"]["names"] == ["ArenaChannel"]
    assert detail["research_brief"]["numbers"] == ["40"]
    assert detail["people"]
    assert detail["popular"]
    assert detail["research_brief"]["popular_videos"][0]["title"] == "Radiant grind"
    assert seen == {"query": "Valorant gameplay", "exclude": "abcdefghijk"}
    assert any("Inside Valorant" in concept["background"] for concept in detail["concepts"])


def _metadata() -> YoutubeMetadata:
    return YoutubeMetadata(
        video_id="abcdefghijk",
        title="Valorant Radiant",
        author="ArenaChannel",
        thumbnail_url="https://i.ytimg.com/vi/abcdefghijk/hqdefault.jpg",
    )


def _jpeg() -> bytes:
    image = Image.new("RGB", (640, 360), (20, 40, 80))
    for x in range(80, 180):
        for y in range(40, 180):
            image.putpixel((x, y), (234, 192, 157))
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=95)
    return buffer.getvalue()


def _video(video_id: str, title: str, views: int, thumbnail: str = "") -> dict:
    return {
        "id": video_id,
        "snippet": {
            "title": title,
            "thumbnails": {"high": {"url": thumbnail or f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"}},
        },
        "statistics": {"viewCount": str(views)},
    }
