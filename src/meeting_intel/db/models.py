from datetime import datetime
from uuid import uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=False, default="user")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class MeetingModel(Base):
    __tablename__ = "meetings"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_uri: Mapped[str | None] = mapped_column(Text)
    meeting_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    participants: Mapped[list] = mapped_column(JSONB().with_variant(JSON, "sqlite"), nullable=False, default=list)
    transcript: Mapped[list] = mapped_column(JSONB().with_variant(JSON, "sqlite"), nullable=False, default=list)
    analysis_metadata: Mapped[dict] = mapped_column(JSONB().with_variant(JSON, "sqlite"), nullable=False, default=dict)
    normalized_schema_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="v1",
    )
    created_by: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    summary: Mapped["SummaryModel | None"] = relationship(
        "SummaryModel",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
        back_populates="meeting",
    )
    action_items: Mapped[list["ActionItemModel"]] = relationship(
        "ActionItemModel",
        cascade="all, delete-orphan",
        passive_deletes=True,
        back_populates="meeting",
    )
    decisions: Mapped[list["DecisionModel"]] = relationship(
        "DecisionModel",
        cascade="all, delete-orphan",
        passive_deletes=True,
        back_populates="meeting",
    )
    risks: Mapped[list["RiskModel"]] = relationship(
        "RiskModel",
        cascade="all, delete-orphan",
        passive_deletes=True,
        back_populates="meeting",
    )
    follow_ups: Mapped[list["FollowUpModel"]] = relationship(
        "FollowUpModel",
        cascade="all, delete-orphan",
        passive_deletes=True,
        back_populates="meeting",
    )


class SummaryModel(Base):
    __tablename__ = "summaries"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    meeting_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    )
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    topics: Mapped[list] = mapped_column(JSONB().with_variant(JSON, "sqlite"), nullable=False, default=list)
    open_questions: Mapped[list] = mapped_column(JSONB().with_variant(JSON, "sqlite"), nullable=False, default=list)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, default="gpt-4o-mini")
    trace_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    meeting: Mapped["MeetingModel"] = relationship(
        "MeetingModel",
        back_populates="summary",
    )


class ActionItemModel(Base):
    __tablename__ = "action_items"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    meeting_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    owner: Mapped[str | None] = mapped_column(String(255))
    due_date: Mapped[datetime | None] = mapped_column(Date)
    priority: Mapped[str] = mapped_column(String(50), nullable=False, default="medium")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open")
    source_quote: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    meeting: Mapped["MeetingModel"] = relationship(
        "MeetingModel",
        back_populates="action_items",
    )


class DecisionModel(Base):
    __tablename__ = "decisions"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    meeting_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    owner: Mapped[str | None] = mapped_column(String(255))
    rationale: Mapped[str | None] = mapped_column(Text)
    source_quote: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    meeting: Mapped["MeetingModel"] = relationship(
        "MeetingModel",
        back_populates="decisions",
    )


class RiskModel(Base):
    __tablename__ = "risks"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    meeting_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="medium")
    probability: Mapped[str] = mapped_column(String(50), nullable=False, default="medium")
    mitigation: Mapped[str | None] = mapped_column(Text)
    owner: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    meeting: Mapped["MeetingModel"] = relationship(
        "MeetingModel",
        back_populates="risks",
    )


class FollowUpModel(Base):
    __tablename__ = "follow_ups"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    meeting_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    )
    recipient: Mapped[str | None] = mapped_column(Text)
    subject: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    tone: Mapped[str] = mapped_column(String(50), nullable=False, default="professional")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    meeting: Mapped["MeetingModel"] = relationship(
        "MeetingModel",
        back_populates="follow_ups",
    )


class EmbeddingMetadataModel(Base):
    __tablename__ = "embedding_metadata"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    meeting_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    collection_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="meeting_memory",
    )
    embedding_model: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="hash-embedding-384",
    )
    artifact_type: Mapped[str] = mapped_column(String(50), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    token_count: Mapped[int | None] = mapped_column(Integer)
    source_type: Mapped[str | None] = mapped_column(String(50))
    metadata_json: Mapped[dict] = mapped_column("metadata", JSONB().with_variant(JSON, "sqlite"), nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class ConversationHistoryModel(Base):
    __tablename__ = "conversation_history"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    meeting_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="SET NULL"),
    )
    user_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    conversation_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    retrieved_chunk_ids: Mapped[list] = mapped_column(JSONB().with_variant(JSON, "sqlite"), nullable=False, default=list)
    trace_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
