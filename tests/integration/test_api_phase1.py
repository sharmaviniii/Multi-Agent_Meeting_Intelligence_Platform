from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient

from meeting_intel.api.app import create_app
from meeting_intel.api.dependencies import intelligence_dep, repository_dep
from meeting_intel.core.config import Settings
from meeting_intel.db.models import Base
from meeting_intel.db.repository import SQLAlchemyMeetingRepository
from meeting_intel.ingestion.parsers import parse_transcript_text
from meeting_intel.schemas import ActionItem, Decision, FollowUp, Risk
from meeting_intel.services.llm import LLMClient
from meeting_intel.services.meeting_intelligence import MeetingIntelligenceService


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


def test_upload_analysis_and_retrieval_with_sqlalchemy_repository(tmp_path):
    db_path = tmp_path / 'test_api.db'
    engine = create_engine(f'sqlite:///{db_path}', future=True)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    repo = SQLAlchemyMeetingRepository(session_factory)

    app = create_app()
    app.dependency_overrides[repository_dep] = lambda: repo

    client = TestClient(app)
    transcript = (
        "Asha: We need the demo ready by Friday.\n"
        "Rahul: I will finish the API by Friday.\n"
        "Mina: We agreed to ship behind a feature flag.\n"
        "Asha: Vendor access is a risk for QA."
    )

    upload_response = client.post(
        "/upload",
        json={"title": "SQLAlchemy Demo", "text": transcript, "participants": ["Asha", "Rahul"]},
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
    assert email_response.json()["email"]["subject"] == "Follow-up: SQLAlchemy Demo"

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


def test_upload_marks_llm_analysis_mode_when_provider_succeeds():
    class AvailableLLM:
        client = object()

    class SuccessfulIntelligence:
        llm = AvailableLLM()

        async def summarize(self, meeting):
            return "LLM summary"

        async def extract_action_items(self, meeting):
            return [ActionItem(description="Finish the API", owner="Rahul")]

        async def extract_decisions(self, meeting):
            return [Decision(description="Ship behind a feature flag")]

        async def extract_risks(self, meeting):
            return [Risk(description="Vendor access may block QA")]

        async def draft_follow_up_email(self, *args, **kwargs):
            return FollowUp(subject="Follow-up", body="Thanks team.")

    app = create_app()
    app.dependency_overrides[intelligence_dep] = lambda: SuccessfulIntelligence()
    client = TestClient(app)

    response = client.post(
        "/upload",
        json={"title": "LLM", "text": "Asha: We agreed to ship behind a feature flag."},
    )

    assert response.status_code == 200
    meeting = response.json()["meeting"]
    assert meeting["summary"] == "LLM summary"
    assert meeting["embeddings_metadata"]["analysis_mode"] == "llm"


def test_openai_failure_falls_back_to_heuristic_analysis():
    fallback = MeetingIntelligenceService(Settings(offline_mode=True), LLMClient(Settings()))

    class BrokenIntelligence:
        llm = type("UnavailableLLM", (), {"client": object()})()

        async def summarize(self, meeting):
            raise RuntimeError("provider rate limited")

        def generate_heuristic_analysis(self, meeting):
            fallback.generate_heuristic_analysis(meeting)

    app = create_app()
    app.dependency_overrides[intelligence_dep] = lambda: BrokenIntelligence()
    client = TestClient(app)

    response = client.post(
        "/upload",
        json={
            "title": "Fallback",
            "text": (
                "Asha: We need the demo ready by Friday.\n"
                "Rahul: I will finish the API by Friday.\n"
                "Mina: We agreed to ship behind a feature flag.\n"
                "Asha: Vendor access is a risk for QA."
            ),
        },
    )

    assert response.status_code == 200
    meeting = response.json()["meeting"]
    assert meeting["summary"]
    assert meeting["action_items"]
    assert meeting["decisions"]
    assert meeting["risks"]
    assert meeting["follow_ups"]
    assert meeting["embeddings_metadata"]["analysis_mode"] == "heuristic"


def test_upload_succeeds_when_provider_unavailable():
    response = TestClient(create_app()).post(
        "/upload",
        json={"title": "No Provider", "text": "Asha: We need the demo ready by Friday."},
    )

    assert response.status_code == 200
    assert response.json()["meeting"]["embeddings_metadata"]["analysis_mode"] == "heuristic"
