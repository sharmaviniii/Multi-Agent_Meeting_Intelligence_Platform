from fastapi.testclient import TestClient

from meeting_intel.api.app import create_app
from meeting_intel.api.dependencies import intelligence_dep


def test_upload_summarize_and_ask_offline():
    client = TestClient(create_app())
    transcript = "Asha: We need the demo ready by Friday.\nRahul: I will finish the API."

    upload_response = client.post(
        "/upload",
        json={"title": "Demo", "text": transcript, "participants": ["Asha", "Rahul"]},
    )
    assert upload_response.status_code == 200
    meeting_id = upload_response.json()["meeting"]["meeting_id"]

    summarize_response = client.post("/summarize", json={"meeting_id": meeting_id})
    assert summarize_response.status_code == 200
    assert summarize_response.json()["meeting"]["summary"].startswith("Offline summary")

    ask_response = client.post(
        "/ask",
        json={"meeting_id": meeting_id, "question": "Who will finish the API?", "top_k": 3},
    )
    assert ask_response.status_code == 200
    assert "sources" in ask_response.json()


def test_upload_accepts_multipart_transcript_file():
    client = TestClient(create_app())
    transcript = b"Asha: We need the demo ready by Friday.\nRahul: I will finish the API."

    upload_response = client.post(
        "/upload",
        files={"file": ("demo.txt", transcript, "text/plain")},
    )

    assert upload_response.status_code == 200
    meeting = upload_response.json()["meeting"]
    assert meeting["title"] == "demo"
    assert meeting["source_type"] == "txt"
    assert meeting["transcript"][0]["speaker"] == "Asha"


def test_upload_openapi_schema_advertises_file_upload():
    client = TestClient(create_app())

    upload_schema = client.get("/openapi.json").json()["paths"]["/upload"]["post"]

    assert "multipart/form-data" in upload_schema["requestBody"]["content"]
    schema_ref = upload_schema["requestBody"]["content"]["multipart/form-data"]["schema"]["$ref"]
    schema_name = schema_ref.rsplit("/", 1)[-1]
    file_schema = client.get("/openapi.json").json()["components"]["schemas"][schema_name][
        "properties"
    ]["file"]
    file_variants = file_schema.get("anyOf", [file_schema])
    assert {
        "type": "string",
        "contentMediaType": "application/octet-stream",
    } in file_variants


def test_phase2_structured_intelligence_endpoints_offline():
    client = TestClient(create_app())
    transcript = (
        "Asha: We need the demo ready by Friday.\n"
        "Rahul: I will finish the API by Friday.\n"
        "Mina: We agreed to ship behind a feature flag.\n"
        "Asha: Vendor access is a risk for QA."
    )

    upload_response = client.post(
        "/upload",
        json={"title": "Phase 2 Demo", "text": transcript, "participants": ["Asha", "Rahul"]},
    )
    assert upload_response.status_code == 200
    meeting_id = upload_response.json()["meeting"]["meeting_id"]

    action_response = client.post("/action-items", json={"meeting_id": meeting_id})
    assert action_response.status_code == 200
    assert action_response.json()["meeting_id"] == meeting_id
    assert action_response.json()["action_items"]

    decisions_response = client.post("/decisions", json={"meeting_id": meeting_id})
    assert decisions_response.status_code == 200
    assert decisions_response.json()["decisions"]

    risks_response = client.post("/risks", json={"meeting_id": meeting_id})
    assert risks_response.status_code == 200
    assert risks_response.json()["risks"]

    email_response = client.post(
        "/email-draft",
        json={"meeting_id": meeting_id, "audience": "team", "tone": "professional"},
    )
    assert email_response.status_code == 200
    assert email_response.json()["email"]["subject"] == "Follow-up: Phase 2 Demo"

    meeting_response = client.get(f"/meetings/{meeting_id}")
    meeting = meeting_response.json()["meeting"]
    assert meeting["action_items"]
    assert meeting["decisions"]
    assert meeting["risks"]
    assert meeting["follow_ups"]


def test_fresh_upload_populates_every_workspace_tab():
    client = TestClient(create_app())
    transcript = (
        "Asha: We need the demo ready by Friday.\n"
        "Rahul: I will finish the API by Friday.\n"
        "Mina: We agreed to ship behind a feature flag.\n"
        "Asha: Vendor access is a risk for QA."
    )

    upload_response = client.post(
        "/upload",
        json={"title": "Workspace Ready", "text": transcript, "participants": ["Asha", "Rahul"]},
    )

    assert upload_response.status_code == 200
    uploaded_meeting = upload_response.json()["meeting"]
    meeting_id = uploaded_meeting["meeting_id"]
    assert uploaded_meeting["summary"]
    assert uploaded_meeting["action_items"]
    assert uploaded_meeting["decisions"]
    assert uploaded_meeting["risks"]
    assert uploaded_meeting["follow_ups"]

    transcript_response = client.get(f"/transcript/{meeting_id}")
    assert transcript_response.status_code == 200
    assert transcript_response.json()["meeting"]["transcript"]

    summary_response = client.get(f"/summary/{meeting_id}")
    assert summary_response.status_code == 200
    assert summary_response.json()["meeting"]["summary"]

    action_response = client.get(f"/action-items/{meeting_id}")
    assert action_response.status_code == 200
    assert action_response.json()["action_items"]

    decisions_response = client.get(f"/decisions/{meeting_id}")
    assert decisions_response.status_code == 200
    assert decisions_response.json()["decisions"]

    risks_response = client.get(f"/risks/{meeting_id}")
    assert risks_response.status_code == 200
    assert risks_response.json()["risks"]

    email_response = client.get(f"/email-draft/{meeting_id}")
    assert email_response.status_code == 200
    assert email_response.json()["email"]["body"]


def test_analysis_generation_failure_returns_503():
    class BrokenIntelligence:
        async def summarize(self, meeting):
            raise RuntimeError("provider down")

    app = create_app()
    app.dependency_overrides[intelligence_dep] = lambda: BrokenIntelligence()
    client = TestClient(app)

    response = client.post("/upload", json={"title": "Broken", "text": "Asha: Hello"})

    assert response.status_code == 503
    assert response.json()["detail"] == "LLM provider unavailable while generating meeting analysis"
