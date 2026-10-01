from io import BytesIO

from PIL import Image

from app.domain.state import DesignSpec, TextSpec
from app.tools.compositor import compose
from app.tools.image_generation import thumbnail_prompt
from app.tools.portraits import subject_portrait
from app.tools.youtube import video_still_bytes


def test_project_stores_a_creative_style(client):
    created = client.post(
        "/api/projects",
        json={"description": "I compared ten editors on one timeline.", "creative_style": "ghibli"},
    )
    assert created.status_code == 201
    assert created.json()["creative_style"] == "ghibli"
    updated = client.patch(f"/api/projects/{created.json()['id']}", json={"creative_style": "gaming"})
    assert updated.json()["creative_style"] == "gaming"
    rejected = client.post(
        "/api/projects",
        json={"description": "I compared ten editors on one timeline.", "creative_style": "oil-paint"},
    )
    assert rejected.status_code == 422


def test_ghibli_prompt_names_the_style_and_keeps_a_person_slot():
    spec = DesignSpec(
        subject={"position": "right", "style": "ghibli", "portrait": True, "description": "a forest path"},
        background={"description": "tall trees"},
        text=TextSpec(content="LOST", position="left"),
    )
    prompt = thumbnail_prompt(spec)
    assert "Ghibli-inspired" in prompt
    assert "Do not draw a person" in prompt


def test_subject_portrait_crops_the_brighter_side():
    image = Image.new("RGB", (400, 200), "black")
    image.paste(Image.new("RGB", (200, 200), "white"), (0, 0))
    crop = subject_portrait(image)
    assert crop.getpixel((4, 4)) == (255, 255, 255)


def test_compose_places_a_creator_photo_on_the_subject_side():
    background = Image.new("RGB", (1280, 720), "black")
    portrait = Image.new("RGB", (80, 120), (220, 30, 30))
    spec = DesignSpec(subject={"position": "right"}, text=TextSpec(content="HI", position="left"))
    image = compose(background, spec, people=[portrait])
    assert image.getpixel((1100, 300))[0] > 150


def test_video_still_skips_the_tiny_placeholder(monkeypatch):
    calls: list[str] = []

    def fake_download(url: str) -> bytes | None:
        calls.append(url)
        image = Image.new("RGB", (120, 90) if "maxres" in url else (640, 360), "white")
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        return buffer.getvalue()

    monkeypatch.setattr("app.tools.youtube.download_bytes", fake_download)
    data = video_still_bytes("abc", "https://i.ytimg.com/vi/abc/hqdefault.jpg")
    assert data is not None
    assert Image.open(BytesIO(data)).width == 640
    assert any("maxresdefault" in url for url in calls)
