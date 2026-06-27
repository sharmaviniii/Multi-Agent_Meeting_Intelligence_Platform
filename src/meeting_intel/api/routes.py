from uuid import UUID

from fastapi import APIRouter, Depends

from meeting_intel.api.dependencies import intelligence_dep, repository_dep, settings_dep, vector_store_dep
from meeting_intel.api.errors import NotFoundError
from meeting_intel.core.config import Settings
from meeting_intel.db.repository import InMemoryMeetingRepository
from meeting_intel.ingestion.meetingbank import ingest_meetingbank
from meeting_intel.ingestion.parsers import parse_transcript_text
from meeting_intel.rag.chunking import chunk_meeting
from meeting_intel.rag.vector_store import ChromaMeetingStore, rerank
from meeting_intel.schemas import AskRequest, AskResponse, MeetingResponse, SummarizeRequest, UploadRequest
from meeting_intel.services.meeting_intelligence import MeetingIntelligenceService

router = APIRouter()


@router.post("/upload", response_model=MeetingResponse)
async def upload(
    payload: UploadRequest,
    settings: Settings = Depends(settings_dep),
    repo: InMemoryMeetingRepository = Depends(repository_dep),
    store: ChromaMeetingStore = Depends(vector_store_dep),
):
    meeting = parse_transcript_text(
        payload.text,
        title=payload.title,
        source_type=payload.source_type,
        participants=payload.participants,
    )
    chunks = chunk_meeting(meeting, settings.chunk_max_chars, settings.chunk_overlap_chars)
    store.upsert_chunks(chunks)
    meeting.embeddings_metadata = {
        "collection": settings.chroma_collection,
        "embedding_model": settings.embedding_model if not settings.offline_mode else "mock-embedding",
        "chunk_count": len(chunks),
        "offline_mode": settings.offline_mode,
    }
    await repo.save(meeting)
    return MeetingResponse(meeting=meeting)


@router.post("/summarize", response_model=MeetingResponse)
async def summarize(
    payload: SummarizeRequest,
    settings: Settings = Depends(settings_dep),
    repo: InMemoryMeetingRepository = Depends(repository_dep),
    store: ChromaMeetingStore = Depends(vector_store_dep),
    intelligence: MeetingIntelligenceService = Depends(intelligence_dep),
):
    if payload.meeting_id:
        meeting = await repo.get(payload.meeting_id)
        if meeting is None:
            raise NotFoundError(f"Meeting {payload.meeting_id} was not found")
    else:
        if not payload.text:
            raise NotFoundError("Either meeting_id or text is required")
        meeting = parse_transcript_text(
            payload.text,
            title=payload.title or "Untitled Meeting",
            source_type=payload.source_type,
            participants=payload.participants,
        )
    chunks = chunk_meeting(meeting, settings.chunk_max_chars, settings.chunk_overlap_chars)
    store.upsert_chunks(chunks)
    meeting.summary = await intelligence.summarize(meeting)
    meeting.embeddings_metadata = {
        "collection": settings.chroma_collection,
        "embedding_model": settings.embedding_model if not settings.offline_mode else "mock-embedding",
        "chunk_count": len(chunks),
        "offline_mode": settings.offline_mode,
        "summarization_strategy": (
            "map_reduce"
            if len(meeting.transcript_text) > settings.max_transcript_chars_for_direct_summary
            else "direct"
        ),
    }
    await repo.save(meeting)
    return MeetingResponse(meeting=meeting)


@router.post("/ask", response_model=AskResponse)
async def ask(
    payload: AskRequest,
    store: ChromaMeetingStore = Depends(vector_store_dep),
    intelligence: MeetingIntelligenceService = Depends(intelligence_dep),
):
    hits = store.search(
        payload.question,
        top_k=min(payload.top_k * 4, 20),
        meeting_id=str(payload.meeting_id) if payload.meeting_id else None,
        artifact_type="transcript",
    )
    ranked_hits = rerank(payload.question, hits)[: payload.top_k]
    context = "\n\n".join(hit["text"] for hit in ranked_hits)
    answer = await intelligence.llm.answer(
        "Answer using only the provided meeting context. If context is insufficient, say so.",
        f"Question: {payload.question}\n\nContext:\n{context}",
    )
    return AskResponse(answer=answer, sources=ranked_hits)


@router.post("/ingest/meetingbank")
async def ingest_meetingbank_endpoint(
    settings: Settings = Depends(settings_dep),
    repo: InMemoryMeetingRepository = Depends(repository_dep),
    store: ChromaMeetingStore = Depends(vector_store_dep),
):
    meetings = ingest_meetingbank(settings)
    for meeting in meetings:
        chunks = chunk_meeting(meeting, settings.chunk_max_chars, settings.chunk_overlap_chars)
        store.upsert_chunks(chunks)
        meeting.embeddings_metadata = {
            **meeting.embeddings_metadata,
            "collection": settings.chroma_collection,
            "chunk_count": len(chunks),
            "offline_mode": settings.offline_mode,
        }
        await repo.save(meeting)
    return {"ingested": len(meetings), "meeting_ids": [str(meeting.meeting_id) for meeting in meetings]}


@router.get("/meetings/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: UUID,
    repo: InMemoryMeetingRepository = Depends(repository_dep),
):
    meeting = await repo.get(meeting_id)
    if meeting is None:
        raise NotFoundError(f"Meeting {meeting_id} was not found")
    return MeetingResponse(meeting=meeting)
