from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class SourceType(StrEnum):
    raw_text = "raw_text"
    zoom = "zoom"
    teams = "teams"
    google_meet = "google_meet"
    txt = "txt"
    pdf = "pdf"
    docx = "docx"
    meetingbank = "meetingbank"
    ami = "ami"


class TranscriptTurn(BaseModel):
    speaker: str = "Unknown"
    text: str
    start_time: str | None = None
    end_time: str | None = None


class ActionItem(BaseModel):
    description: str
    owner: str | None = None
    due_date: str | None = None
    priority: str = "medium"
    source_quote: str | None = None


class Decision(BaseModel):
    description: str
    owner: str | None = None
    rationale: str | None = None
    source_quote: str | None = None


class Risk(BaseModel):
    description: str
    severity: str = "medium"
    mitigation: str | None = None
    owner: str | None = None


class FollowUp(BaseModel):
    recipient: str | None = None
    subject: str
    body: str


class MeetingDocument(BaseModel):
    meeting_id: UUID = Field(default_factory=uuid4)
    title: str
    date: datetime = Field(default_factory=datetime.utcnow)
    participants: list[str] = Field(default_factory=list)
    transcript: list[TranscriptTurn] = Field(default_factory=list)
    summary: str = ""
    action_items: list[ActionItem] = Field(default_factory=list)
    decisions: list[Decision] = Field(default_factory=list)
    risks: list[Risk] = Field(default_factory=list)
    follow_ups: list[FollowUp] = Field(default_factory=list)
    embeddings_metadata: dict = Field(default_factory=dict)
    source_type: SourceType = SourceType.raw_text

    @property
    def transcript_text(self) -> str:
        return "\n".join(f"{turn.speaker}: {turn.text}" for turn in self.transcript)


class UploadRequest(BaseModel):
    title: str
    text: str
    source_type: SourceType = SourceType.raw_text
    participants: list[str] = Field(default_factory=list)


class SummarizeRequest(BaseModel):
    meeting_id: UUID | None = None
    title: str | None = None
    text: str | None = None
    source_type: SourceType = SourceType.raw_text
    participants: list[str] = Field(default_factory=list)


class MeetingResponse(BaseModel):
    meeting: MeetingDocument


class AskRequest(BaseModel):
    question: str
    meeting_id: UUID | None = None
    top_k: int = Field(default=5, ge=1, le=20)


class AskResponse(BaseModel):
    answer: str
    sources: list[dict] = Field(default_factory=list)


class EmailDraftRequest(BaseModel):
    meeting_id: UUID
    audience: str = "meeting participants"
    tone: str = "professional"
