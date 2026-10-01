from io import BytesIO

from PIL import Image


def _png() -> bytes:
    image = Image.new("RGB", (32, 32), "#224466")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_concept_thumbnail_and_export(client):
    created = client.post(
        "/api/projects",
        json={
            "description": "I tested 20 AI coding tools to see which one can actually replace a developer.",
            "privacy_mode": "local",
        },
    )
    assert created.status_code == 201
    project_id = created.json()["id"]

    uploaded = client.post(
        f"/api/projects/{project_id}/references",
        files=[("files", ("ref.png", _png(), "image/png"))],
    )
    assert uploaded.status_code == 201

    started = client.post(f"/api/projects/{project_id}/generate")
    assert started.status_code == 202
    detail = client.get(f"/api/projects/{project_id}").json()
    assert detail["status"] == "concepts_ready"
    assert len(detail["concepts"]) == 4
    assert detail["references"]

    concept_id = detail["concepts"][0]["id"]
    rendered = client.post(f"/api/projects/{project_id}/concepts/{concept_id}/generate")
    assert rendered.status_code == 202
    detail = client.get(f"/api/projects/{project_id}").json()
    assert detail["status"] == "ready"
    generation = detail["generations"][-1]
    assert generation["critique"]["passed"] is True

    image = client.get(generation["image_url"])
    assert image.status_code == 200
    assert image.headers["content-type"] == "image/png"

    edited = client.patch(
        f"/api/generations/{generation['id']}",
        json={"content": "AI WON", "position": "left", "size": "large", "color": "#f2c14e"},
    )
    assert edited.status_code == 200
    assert edited.json()["design_spec"]["text"]["content"] == "AI WON"

    exported = client.get(f"/api/generations/{generation['id']}/export?format=webp")
    assert exported.status_code == 200
    assert exported.headers["content-type"] == "image/webp"


def test_cloud_mode_requires_a_key(client, monkeypatch):
    monkeypatch.setenv("LLM_MODE", "auto")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    from app.core.config import get_settings

    get_settings.cache_clear()
    created = client.post(
        "/api/projects",
        json={"description": "A quiet documentary about city trains.", "privacy_mode": "cloud"},
    )
    response = client.post(f"/api/projects/{created.json()['id']}/generate")
    assert response.status_code == 400


def test_rejects_a_non_youtube_url(client):
    response = client.post(
        "/api/projects",
        json={"description": "A video about ceramic glazes.", "youtube_url": "https://vimeo.com/1"},
    )
    assert response.status_code == 422
