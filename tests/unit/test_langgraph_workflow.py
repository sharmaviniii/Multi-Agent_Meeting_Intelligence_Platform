import pytest

from meeting_intel.core.config import Settings
from meeting_intel.ingestion.parsers import parse_transcript_text
from meeting_intel.orchestration import MeetingIntelligenceWorkflow
from meeting_intel.rag.chunking import chunk_meeting
from meeting_intel.rag.embeddings import MockEmbeddingModel
from meeting_intel.rag.vector_store import ChromaMeetingStore
from meeting_intel.services.llm import LLMClient
from meeting_intel.services.meeting_intelligence import MeetingIntelligenceService


def _workflow() -> tuple[MeetingIntelligenceWorkflow, Settings]:
    settings = Settings(offline_mode=True)
    store = ChromaMeetingStore(settings, MockEmbeddingModel())
    intelligence = MeetingIntelligenceService(settings, LLMClient(settings))
    return MeetingIntelligenceWorkflow(store, intelligence), settings


@pytest.mark.asyncio
async def test_langgraph_workflow_answers_with_retrieved_sources_offline():
    workflow, settings = _workflow()
    meeting = parse_transcript_text(
        "Asha: We need the demo ready by Friday.\nRahul: I will finish the API.",
        title="Demo",
        participants=["Asha", "Rahul"],
    )
    workflow.store.upsert_chunks(
        chunk_meeting(meeting, settings.chunk_max_chars, settings.chunk_overlap_chars)
    )

    result = await workflow.run(
        question="Who will finish the API?",
        meeting_id=str(meeting.meeting_id),
        top_k=3,
    )

    assert result["answer"].startswith("Offline answer based on retrieved context")
    assert result["sources"]


@pytest.mark.asyncio
async def test_langgraph_workflow_routes_explicit_action_item_intent():
    workflow, _ = _workflow()
    meeting = parse_transcript_text(
        "Asha: We need the demo ready by Friday.\nRahul: I will finish the API by Friday.",
        title="Demo",
        participants=["Asha", "Rahul"],
    )

    result = await workflow.run(
        question="Extract action items",
        meeting=meeting,
        intent="action_items",
    )

    assert result["action_items"]
    assert result["action_items"][0].owner in {"Asha", "Rahul"}


@pytest.mark.asyncio
async def test_langgraph_workflow_routes_email_draft_intent_offline():
    workflow, _ = _workflow()
    meeting = parse_transcript_text(
        "Mina: We agreed to ship behind a feature flag.",
        title="Launch Review",
        participants=["Mina"],
    )

    result = await workflow.run(
        question="Draft follow-up email",
        meeting=meeting,
        intent="email_draft",
        audience="team",
    )

    assert result["email"].subject == "Follow-up: Launch Review"
    assert result["email"].recipient == "team"
