from meeting_intel.core.config import Settings
from meeting_intel.ingestion.parsers import parse_transcript_text
from meeting_intel.rag.chunking import chunk_meeting
from meeting_intel.rag.embeddings import get_embedding_model
from meeting_intel.rag.vector_store import ChromaMeetingStore, rerank


def test_offline_vector_store_retrieves_relevant_chunk():
    settings = Settings(offline_mode=True)
    embeddings = get_embedding_model(settings.embedding_model, offline_mode=True)
    store = ChromaMeetingStore(settings, embeddings)
    meeting = parse_transcript_text(
        "Asha: The payments API must be ready Friday.\n"
        "Rahul: The analytics dashboard can wait.",
        title="Retrieval Demo",
    )

    store.upsert_chunks(chunk_meeting(meeting, max_chars=80, overlap=10))
    hits = store.search("payments API Friday", meeting_id=str(meeting.meeting_id), top_k=3)

    assert hits
    assert any("payments" in hit["text"].lower() for hit in hits)


def test_rerank_prefers_lexical_matches():
    hits = [
        {"text": "analytics dashboard", "score": 0.9},
        {"text": "payments API Friday", "score": 0.5},
    ]

    ranked = rerank("payments API Friday", hits)

    assert ranked[0]["text"] == "payments API Friday"
