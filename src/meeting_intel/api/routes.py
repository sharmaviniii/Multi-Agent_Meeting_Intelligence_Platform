from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from meeting_intel.api.dependencies import (
    intelligence_dep,
    rate_limit_dep,
    repository_dep,
    settings_dep,
    vector_store_dep,
)
from meeting_intel.api.errors import NotFoundError
from meeting_intel.core.config import Settings
from meeting_intel.db.repository import MeetingRepository
from meeting_intel.ingestion.meetingbank import ingest_meetingbank
from meeting_intel.ingestion.parsers import parse_file, parse_transcript_text
from meeting_intel.orchestration import MeetingIntelligenceWorkflow
from meeting_intel.rag.chunking import chunk_meeting
from meeting_intel.rag.vector_store import ChromaMeetingStore
from meeting_intel.schemas import (
    ActionItemsResponse,
    AskRequest,
    AskResponse,
    DecisionsResponse,
    EmailDraftRequest,
    EmailDraftResponse,
    MeetingIdRequest,
    MeetingResponse,
    RisksResponse,
    SummarizeRequest,
    UploadRequest,
)
from meeting_intel.services.meeting_intelligence import MeetingIntelligenceService

router = APIRouter()
SETTINGS_DEP = Depends(settings_dep)
REPOSITORY_DEP = Depends(repository_dep)
VECTOR_STORE_DEP = Depends(vector_store_dep)
INTELLIGENCE_DEP = Depends(intelligence_dep)
RATE_LIMIT_DEP = Depends(rate_limit_dep)


async def _get_existing_meeting(meeting_id: UUID, repo: MeetingRepository):
    meeting = await repo.get(meeting_id)
    if meeting is None:
        raise NotFoundError(f"Meeting {meeting_id} was not found")
    return meeting


@router.post("/upload", response_model=MeetingResponse)
async def upload(
    request: Request,
    file: UploadFile | None = File(None),
    settings: Settings = SETTINGS_DEP,
    repo: MeetingRepository = REPOSITORY_DEP,
    store: ChromaMeetingStore = VECTOR_STORE_DEP,
    intelligence: MeetingIntelligenceService = INTELLIGENCE_DEP,
    __: None = RATE_LIMIT_DEP,
):
    meeting = await _parse_upload_request(request, file)
    _index_meeting_chunks(meeting, settings, store)
    await _generate_full_analysis(meeting, store, intelligence)
    await repo.save(meeting)
    return MeetingResponse(meeting=meeting)


def _index_meeting_chunks(
    meeting,
    settings: Settings,
    store: ChromaMeetingStore,
) -> None:
    chunks = chunk_meeting(meeting, settings.chunk_max_chars, settings.chunk_overlap_chars)
    store.upsert_chunks(chunks)
    meeting.embeddings_metadata = {
        "collection": settings.chroma_collection,
        "embedding_model": settings.embedding_model,
        "chunk_count": len(chunks),
        "offline_mode": settings.offline_mode,
        "analysis_generated": meeting.embeddings_metadata.get("analysis_generated", False),
    }


async def _generate_full_analysis(
    meeting,
    store: ChromaMeetingStore,
    intelligence: MeetingIntelligenceService,
) -> None:
    workflow = MeetingIntelligenceWorkflow(store, intelligence)
    try:
        if not meeting.summary:
            result = await workflow.run(
                question="Summarize this meeting",
                meeting=meeting,
                intent="summarization",
            )
            meeting.summary = result.get("summary", "")

        if not meeting.action_items:
            result = await workflow.run(
                question="Extract action items",
                meeting=meeting,
                intent="action_items",
            )
            meeting.action_items = result.get("action_items", [])

        if not meeting.decisions:
            result = await workflow.run(
                question="Extract decisions",
                meeting=meeting,
                intent="decisions",
            )
            meeting.decisions = result.get("decisions", [])

        if not meeting.risks:
            result = await workflow.run(
                question="Extract risks",
                meeting=meeting,
                intent="risks",
            )
            meeting.risks = result.get("risks", [])

        if not meeting.follow_ups:
            result = await workflow.run(
                question="Draft follow-up email",
                meeting=meeting,
                intent="email_draft",
            )
            email = result.get("email")
            if email is not None:
                meeting.follow_ups = [email]
        meeting.embeddings_metadata["analysis_mode"] = (
            "llm" if _llm_available(intelligence) else "heuristic"
        )
    except Exception:
        intelligence.generate_heuristic_analysis(meeting)
        meeting.embeddings_metadata["analysis_mode"] = "heuristic"

    meeting.embeddings_metadata["analysis_generated"] = True


def _llm_available(intelligence: MeetingIntelligenceService) -> bool:
    return getattr(getattr(intelligence, "llm", None), "client", None) is not None


async def _run_analysis_workflow(workflow: MeetingIntelligenceWorkflow, **kwargs):
    try:
        return await workflow.run(**kwargs)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM provider unavailable while generating meeting analysis",
        ) from exc


async def _parse_upload_request(request: Request, upload_file: UploadFile | None):
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("multipart/form-data"):
        if upload_file is None:
            raise NotFoundError("A transcript file is required")
        suffix = Path(upload_file.filename or "meeting.txt").suffix.lower()
        with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(await upload_file.read())
        try:
            return parse_file(temp_path, title=Path(upload_file.filename or "Meeting").stem)
        finally:
            temp_path.unlink(missing_ok=True)

    payload = UploadRequest.model_validate(await request.json())
    return parse_transcript_text(
        payload.text,
        title=payload.title,
        source_type=payload.source_type,
        participants=payload.participants,
    )


@router.post("/summarize", response_model=MeetingResponse)
async def summarize(
    payload: SummarizeRequest,
    settings: Settings = SETTINGS_DEP,
    repo: MeetingRepository = REPOSITORY_DEP,
    store: ChromaMeetingStore = VECTOR_STORE_DEP,
    intelligence: MeetingIntelligenceService = INTELLIGENCE_DEP,
    __: None = RATE_LIMIT_DEP,
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
    _index_meeting_chunks(meeting, settings, store)
    workflow = MeetingIntelligenceWorkflow(store, intelligence)
    result = await _run_analysis_workflow(
        workflow,
        question="Summarize this meeting",
        meeting=meeting,
        intent="summarization",
    )
    meeting.summary = result.get("summary", "")
    meeting.embeddings_metadata["summarization_strategy"] = (
        "map_reduce"
        if len(meeting.transcript_text) > settings.max_transcript_chars_for_direct_summary
        else "direct"
    )
    await repo.save(meeting)
    return MeetingResponse(meeting=meeting)


@router.post("/ask", response_model=AskResponse)
async def ask(
    payload: AskRequest,
    store: ChromaMeetingStore = VECTOR_STORE_DEP,
    intelligence: MeetingIntelligenceService = INTELLIGENCE_DEP,
    __: None = RATE_LIMIT_DEP,
):
    workflow = MeetingIntelligenceWorkflow(store, intelligence)
    result = await _run_analysis_workflow(
        workflow,
        question=payload.question,
        top_k=payload.top_k,
        meeting_id=str(payload.meeting_id) if payload.meeting_id else None,
    )
    return AskResponse(answer=result.get("answer", ""), sources=result.get("sources", []))


@router.post("/action-items", response_model=ActionItemsResponse)
async def action_items(
    payload: MeetingIdRequest,
    repo: MeetingRepository = REPOSITORY_DEP,
    store: ChromaMeetingStore = VECTOR_STORE_DEP,
    intelligence: MeetingIntelligenceService = INTELLIGENCE_DEP,
    __: None = RATE_LIMIT_DEP,
):
    meeting = await _get_existing_meeting(payload.meeting_id, repo)
    workflow = MeetingIntelligenceWorkflow(store, intelligence)
    result = await _run_analysis_workflow(
        workflow,
        question="Extract action items",
        meeting=meeting,
        intent="action_items",
    )
    meeting.action_items = result.get("action_items", [])
    await repo.save(meeting)
    return ActionItemsResponse(meeting_id=meeting.meeting_id, action_items=meeting.action_items)


@router.post("/decisions", response_model=DecisionsResponse)
async def decisions(
    payload: MeetingIdRequest,
    repo: MeetingRepository = REPOSITORY_DEP,
    store: ChromaMeetingStore = VECTOR_STORE_DEP,
    intelligence: MeetingIntelligenceService = INTELLIGENCE_DEP,
    __: None = RATE_LIMIT_DEP,
):
    meeting = await _get_existing_meeting(payload.meeting_id, repo)
    workflow = MeetingIntelligenceWorkflow(store, intelligence)
    result = await _run_analysis_workflow(
        workflow,
        question="Extract decisions",
        meeting=meeting,
        intent="decisions",
    )
    meeting.decisions = result.get("decisions", [])
    await repo.save(meeting)
    return DecisionsResponse(meeting_id=meeting.meeting_id, decisions=meeting.decisions)


@router.post("/risks", response_model=RisksResponse)
async def risks(
    payload: MeetingIdRequest,
    repo: MeetingRepository = REPOSITORY_DEP,
    store: ChromaMeetingStore = VECTOR_STORE_DEP,
    intelligence: MeetingIntelligenceService = INTELLIGENCE_DEP,
    __: None = RATE_LIMIT_DEP,
):
    meeting = await _get_existing_meeting(payload.meeting_id, repo)
    workflow = MeetingIntelligenceWorkflow(store, intelligence)
    result = await _run_analysis_workflow(
        workflow,
        question="Extract risks",
        meeting=meeting,
        intent="risks",
    )
    meeting.risks = result.get("risks", [])
    await repo.save(meeting)
    return RisksResponse(meeting_id=meeting.meeting_id, risks=meeting.risks)


@router.post("/email-draft", response_model=EmailDraftResponse)
async def email_draft(
    payload: EmailDraftRequest,
    repo: MeetingRepository = REPOSITORY_DEP,
    store: ChromaMeetingStore = VECTOR_STORE_DEP,
    intelligence: MeetingIntelligenceService = INTELLIGENCE_DEP,
    __: None = RATE_LIMIT_DEP,
):
    meeting = await _get_existing_meeting(payload.meeting_id, repo)
    workflow = MeetingIntelligenceWorkflow(store, intelligence)
    result = await _run_analysis_workflow(
        workflow,
        question="Draft follow-up email",
        meeting=meeting,
        intent="email_draft",
        audience=payload.audience,
        tone=payload.tone,
        include_sections=payload.include_sections,
    )
    email = result.get("email")
    if email is None:
        raise NotFoundError("Email draft not generated yet")
    meeting.follow_ups = [email]
    await repo.save(meeting)
    return EmailDraftResponse(meeting_id=meeting.meeting_id, email=email)


@router.post("/ingest/meetingbank")
async def ingest_meetingbank_endpoint(
    settings: Settings = SETTINGS_DEP,
    repo: MeetingRepository = REPOSITORY_DEP,
    store: ChromaMeetingStore = VECTOR_STORE_DEP,
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
    return {
        "ingested": len(meetings),
        "meeting_ids": [str(meeting.meeting_id) for meeting in meetings],
    }


@router.get("/meetings/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: UUID,
    repo: MeetingRepository = REPOSITORY_DEP,
):
    meeting = await repo.get(meeting_id)
    if meeting is None:
        raise NotFoundError(f"Meeting {meeting_id} was not found")
    return MeetingResponse(meeting=meeting)


@router.get("/transcript/{meeting_id}", response_model=MeetingResponse)
async def get_transcript(
    meeting_id: UUID,
    repo: MeetingRepository = REPOSITORY_DEP,
):
    meeting = await _get_existing_meeting(meeting_id, repo)
    return MeetingResponse(meeting=meeting)


@router.get("/summary/{meeting_id}", response_model=MeetingResponse)
async def get_summary(
    meeting_id: UUID,
    settings: Settings = SETTINGS_DEP,
    repo: MeetingRepository = REPOSITORY_DEP,
    store: ChromaMeetingStore = VECTOR_STORE_DEP,
    intelligence: MeetingIntelligenceService = INTELLIGENCE_DEP,
):
    meeting = await _get_existing_meeting(meeting_id, repo)
    if not meeting.summary:
        _index_meeting_chunks(meeting, settings, store)
        await _generate_full_analysis(meeting, store, intelligence)
        await repo.save(meeting)
    if not meeting.summary:
        raise NotFoundError("Summary not generated yet")
    return MeetingResponse(meeting=meeting)


@router.get("/action-items/{meeting_id}", response_model=ActionItemsResponse)
async def get_action_items(
    meeting_id: UUID,
    settings: Settings = SETTINGS_DEP,
    repo: MeetingRepository = REPOSITORY_DEP,
    store: ChromaMeetingStore = VECTOR_STORE_DEP,
    intelligence: MeetingIntelligenceService = INTELLIGENCE_DEP,
):
    meeting = await _get_existing_meeting(meeting_id, repo)
    if not meeting.action_items:
        _index_meeting_chunks(meeting, settings, store)
        await _generate_full_analysis(meeting, store, intelligence)
        await repo.save(meeting)
    return ActionItemsResponse(meeting_id=meeting.meeting_id, action_items=meeting.action_items)


@router.get("/decisions/{meeting_id}", response_model=DecisionsResponse)
async def get_decisions(
    meeting_id: UUID,
    settings: Settings = SETTINGS_DEP,
    repo: MeetingRepository = REPOSITORY_DEP,
    store: ChromaMeetingStore = VECTOR_STORE_DEP,
    intelligence: MeetingIntelligenceService = INTELLIGENCE_DEP,
):
    meeting = await _get_existing_meeting(meeting_id, repo)
    if not meeting.decisions:
        _index_meeting_chunks(meeting, settings, store)
        await _generate_full_analysis(meeting, store, intelligence)
        await repo.save(meeting)
    return DecisionsResponse(meeting_id=meeting.meeting_id, decisions=meeting.decisions)


@router.get("/risks/{meeting_id}", response_model=RisksResponse)
async def get_risks(
    meeting_id: UUID,
    settings: Settings = SETTINGS_DEP,
    repo: MeetingRepository = REPOSITORY_DEP,
    store: ChromaMeetingStore = VECTOR_STORE_DEP,
    intelligence: MeetingIntelligenceService = INTELLIGENCE_DEP,
):
    meeting = await _get_existing_meeting(meeting_id, repo)
    if not meeting.risks:
        _index_meeting_chunks(meeting, settings, store)
        await _generate_full_analysis(meeting, store, intelligence)
        await repo.save(meeting)
    return RisksResponse(meeting_id=meeting.meeting_id, risks=meeting.risks)


@router.get("/email-draft/{meeting_id}", response_model=EmailDraftResponse)
async def get_email_draft(
    meeting_id: UUID,
    settings: Settings = SETTINGS_DEP,
    repo: MeetingRepository = REPOSITORY_DEP,
    store: ChromaMeetingStore = VECTOR_STORE_DEP,
    intelligence: MeetingIntelligenceService = INTELLIGENCE_DEP,
):
    meeting = await _get_existing_meeting(meeting_id, repo)
    if not meeting.follow_ups:
        _index_meeting_chunks(meeting, settings, store)
        await _generate_full_analysis(meeting, store, intelligence)
        await repo.save(meeting)
    if not meeting.follow_ups:
        raise NotFoundError("Email draft not generated yet")
    return EmailDraftResponse(meeting_id=meeting.meeting_id, email=meeting.follow_ups[0])


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/live")
async def live():
    return {"status": "live"}


@router.get("/ready")
async def ready(settings: Settings = SETTINGS_DEP):
    return {
        "status": "ready",
        "offline_mode": settings.offline_mode,
        "service": settings.service_name,
    }


@router.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
