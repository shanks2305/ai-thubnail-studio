from io import BytesIO

from PIL import Image


def _png() -> bytes:
    image = Image.new("RGB", (32, 32), "#224466")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _project(client) -> str:
    created = client.post("/api/projects", json={"description": "I tested 20 AI coding tools to see which one can actually replace a developer."})
    project_id = created.json()["id"]
    assert client.post(f"/api/projects/{project_id}/generate").status_code == 202
    return project_id


def test_project_brand_channel_and_style_can_be_deleted(client):
    kit = client.post("/api/brand-kits", json={"name": "Main", "colors": ["#112233", "#ff4d2e", "#f2c14e"], "font": "anton"})
    channel = client.post("/api/channels", json={"name": "Shop"})
    created = client.post(
        "/api/projects",
        json={
            "description": "I tested 20 AI coding tools to see which one can actually replace a developer.",
            "brand_kit_id": kit.json()["id"],
            "channel_id": channel.json()["id"],
        },
    )
    project_id = created.json()["id"]
    assert client.post(f"/api/projects/{project_id}/generate").status_code == 202
    profile = client.post(f"/api/projects/{project_id}/profile", json={"name": "Shop style"})
    assert client.delete(f"/api/brand-kits/{kit.json()['id']}").status_code == 204
    assert client.delete(f"/api/channels/{channel.json()['id']}").status_code == 204
    assert client.delete(f"/api/profiles/{profile.json()['id']}").status_code == 204
    detail = client.get(f"/api/projects/{project_id}").json()
    assert detail["brand_kit_id"] is None
    assert detail["channel_id"] is None
    assert detail["creator_profile_id"] is None
    assert client.get("/api/brand-kits").json() == []
    assert client.get("/api/channels").json() == []
    assert client.get("/api/profiles").json() == []
    assert client.delete(f"/api/projects/{project_id}").status_code == 204
    assert client.get(f"/api/projects/{project_id}").status_code == 404


def test_running_project_cannot_be_deleted(client):
    from app.core.database import session_scope
    from app.db.models import Project

    project_id = _project(client)
    with session_scope() as session:
        project = session.get(Project, project_id)
        assert project is not None
        project.status = "generating"
    assert client.delete(f"/api/projects/{project_id}").status_code == 409


def test_reference_concept_thumbnail_and_test_can_be_deleted(client):
    project_id = _project(client)
    uploaded = client.post(f"/api/projects/{project_id}/references", files=[("files", ("ref.png", _png(), "image/png"))])
    reference_id = uploaded.json()["references"][0]["id"]
    assert client.delete(f"/api/assets/{reference_id}").status_code == 204
    detail = client.get(f"/api/projects/{project_id}").json()
    assert detail["references"] == []
    concept_id = detail["concepts"][0]["id"]
    detail = client.post(f"/api/projects/{project_id}/concepts/{concept_id}/generate")
    assert detail.status_code == 202
    detail = client.get(f"/api/projects/{project_id}").json()
    generation = detail["generations"][-1]
    image_url = generation["image_url"]
    other = detail["concepts"][1]["id"]
    detail = client.post(f"/api/projects/{project_id}/concepts/{other}/generate")
    assert detail.status_code == 202
    detail = client.get(f"/api/projects/{project_id}").json()
    second = detail["generations"][-1]["id"]
    experiment = client.post(
        f"/api/projects/{project_id}/experiments",
        json={"generation_a_id": generation["id"], "generation_b_id": second},
    )
    assert client.delete(f"/api/generations/{generation['id']}").status_code == 204
    assert client.get(image_url).status_code == 404
    detail = client.get(f"/api/projects/{project_id}").json()
    assert all(item["id"] != generation["id"] for item in detail["generations"])
    assert detail["experiments"] == []
    assert client.delete(f"/api/assets/{detail['generations'][-1]['image_url'].rsplit('/', 1)[-1]}").status_code == 400
    assert client.delete(f"/api/concepts/{concept_id}").status_code == 204
    detail = client.get(f"/api/projects/{project_id}").json()
    assert all(item["id"] != concept_id for item in detail["concepts"])
    assert client.delete(f"/api/experiments/{experiment.json()['id']}").status_code == 404
