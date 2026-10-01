def _project(client, description: str = "I tested 20 AI coding tools to see which one can actually replace a developer."):
    created = client.post("/api/projects", json={"description": description})
    assert created.status_code == 201
    project_id = created.json()["id"]
    assert client.post(f"/api/projects/{project_id}/generate").status_code == 202
    detail = client.get(f"/api/projects/{project_id}").json()
    return project_id, detail


def _render(client, project_id: str, concept_id: str):
    assert client.post(f"/api/projects/{project_id}/concepts/{concept_id}/generate").status_code == 202
    return client.get(f"/api/projects/{project_id}").json()


def test_other_concepts_can_render_after_the_first(client):
    project_id, detail = _project(client)
    first, second = detail["concepts"][0]["id"], detail["concepts"][1]["id"]
    detail = _render(client, project_id, first)
    detail = _render(client, project_id, second)
    rendered = {item["concept_id"] for item in detail["generations"]}
    assert first in rendered and second in rendered
    assert detail["status"] == "ready"


def test_new_directions_keep_existing_thumbnails(client):
    project_id, detail = _project(client)
    detail = _render(client, project_id, detail["concepts"][0]["id"])
    kept = detail["generations"][-1]["id"]
    assert client.post(f"/api/projects/{project_id}/directions").status_code == 202
    detail = client.get(f"/api/projects/{project_id}").json()
    assert any(item["id"] == kept for item in detail["generations"])
    assert any(item["archived"] for item in detail["concepts"])
    assert any(not item["archived"] for item in detail["concepts"])
    assert any(run["agent"] == "audience_analyst" and run["status"] == "completed" for run in detail["agent_runs"])


def test_hook_variation_editor_and_prompt(client):
    project_id, detail = _project(client)
    concept_id = detail["concepts"][0]["id"]
    assert client.patch(f"/api/concepts/{concept_id}", json={"image_prompt": "A red workshop door in hard side light"}).status_code == 200
    detail = _render(client, project_id, concept_id)
    generation = detail["generations"][-1]
    assert "red workshop door" in generation["design_spec"]["image_prompt"]
    varied = client.post(f"/api/generations/{generation['id']}/variations", json={"axis": "hook"})
    assert varied.status_code == 200
    assert varied.json()["variation_axis"] == "hook"
    edited = client.patch(
        f"/api/generations/{generation['id']}",
        json={
            "content": "AI WON",
            "position": "left",
            "size": "large",
            "color": "#f2c14e",
            "font": "bebas",
            "stroke": True,
            "vertical": "top",
            "scrim_strength": 0.5,
            "palette": ["#112233", "#ff4d2e", "#f2c14e"],
            "recolor": True,
        },
    )
    text = edited.json()["design_spec"]["text"]
    assert text["font"] == "bebas"
    assert text["stroke"] is True
    assert text["vertical"] == "top"
    assert edited.json()["design_spec"]["recolor"] is True


def test_brand_channel_experiment_and_scores(client):
    kit = client.post(
        "/api/brand-kits",
        json={"name": "Main", "colors": ["#112233", "#ff4d2e", "#f2c14e"], "font": "bebas", "shared": True},
    )
    assert kit.status_code == 201
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
    detail = client.get(f"/api/projects/{project_id}").json()
    saved = client.post(f"/api/projects/{project_id}/profile", json={"name": "Shop style"})
    assert saved.status_code == 201
    learned = client.post(f"/api/channels/{channel.json()['id']}/learn", json={"project_id": project_id})
    assert learned.json()["style_profile"]["style_summary"]
    detail = _render(client, project_id, detail["concepts"][0]["id"])
    detail = _render(client, project_id, detail["concepts"][1]["id"])
    first, second = detail["generations"][0], detail["generations"][-1]
    assert client.patch(f"/api/generations/{first['id']}/performance", json={"impressions": 1000, "clicks": 40}).status_code == 200
    experiment = client.post(
        f"/api/projects/{project_id}/experiments",
        json={"generation_a_id": first["id"], "generation_b_id": second["id"]},
    )
    assert experiment.status_code == 201
    winner = client.patch(f"/api/experiments/{experiment.json()['id']}", json={"winner_id": second["id"], "notes": "Clearer face"})
    assert winner.json()["winner_id"] == second["id"]
    history = client.get(f"/api/channels/{channel.json()['id']}").json()
    assert history["thumbnails"]
    assert any(item["clicks"] == 40 for item in history["thumbnails"])
    restored = client.post(f"/api/generations/{first['id']}/restore")
    assert restored.status_code == 200
    assert client.get(f"/api/projects/{project_id}").json()["selected_generation_id"] == first["id"]


def test_auth_token_hides_projects_from_anonymous_callers(client, monkeypatch):
    from app.core.config import get_settings

    monkeypatch.setenv("AUTH_TOKEN", "studio-secret")
    get_settings.cache_clear()
    assert client.get("/api/projects").status_code == 401
    assert client.get("/api/system").json()["auth_required"] is True
    headers = {"Authorization": "Bearer studio-secret"}
    created = client.post(
        "/api/projects",
        headers=headers,
        json={"description": "A quiet documentary about city trains."},
    )
    assert created.status_code == 201
    assert client.get("/api/projects", headers=headers).json()[0]["id"] == created.json()["id"]
    member = client.post("/api/team/members", headers=headers, json={"name": "Avery"})
    assert member.status_code == 201
    member_headers = {"Authorization": f"Bearer {member.json()['token']}"}
    assert client.get(f"/api/projects/{created.json()['id']}", headers=member_headers).status_code == 404


def test_restart_marks_a_stuck_project_failed(client):
    from app.core.database import session_scope
    from app.db.models import Project
    from app.services.jobs import recover_jobs

    created = client.post("/api/projects", json={"description": "A quiet documentary about city trains."})
    project_id = created.json()["id"]
    with session_scope() as session:
        project = session.get(Project, project_id)
        assert project is not None
        project.status = "analyzing"
    recover_jobs()
    assert client.get(f"/api/projects/{project_id}").json()["status"] == "failed"
