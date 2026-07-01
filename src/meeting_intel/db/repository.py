from collections.abc import Callable
from datetime import UTC, date, datetime
from typing import Protocol
from uuid import UUID

from meeting_intel.schemas import (
    ActionItem,
    Decision,
    FollowUp,
    MeetingDocument,
    Risk,
    TranscriptTurn,
)


class MeetingRepository(Protocol):
    async def save(self, meeting: MeetingDocument) -> MeetingDocument:
        """Persist a meeting document and return the saved document."""
        ...

    async def get(self, meeting_id: UUID) -> MeetingDocument | None:
        """Return a meeting document by ID, or None when it does not exist."""
        ...


class InMemoryMeetingRepository(MeetingRepository):
    def __init__(self) -> None:
        self._meetings: dict[UUID, MeetingDocument] = {}

    async def save(self, meeting: MeetingDocument) -> MeetingDocument:
        self._meetings[meeting.meeting_id] = meeting
        return meeting

    async def get(self, meeting_id: UUID) -> MeetingDocument | None:
        return self._meetings.get(meeting_id)


class SQLAlchemyMeetingRepository(MeetingRepository):
    def __init__(self, session_factory: Callable):
        self.session_factory = session_factory

    async def save(self, meeting: MeetingDocument) -> MeetingDocument:
        from sqlalchemy import delete

        from meeting_intel.db.models import (
            ActionItemModel,
            DecisionModel,
            FollowUpModel,
            MeetingModel,
            RiskModel,
            SummaryModel,
        )

        with self.session_factory() as session:
            existing = session.get(MeetingModel, meeting.meeting_id)
            if existing is None:
                existing = MeetingModel(id=meeting.meeting_id)
                session.add(existing)

            existing.title = meeting.title
            existing.source_type = meeting.source_type.value
            existing.meeting_date = meeting.date
            existing.participants = meeting.participants
            existing.transcript = [turn.model_dump(mode="json") for turn in meeting.transcript]

            session.execute(
                delete(SummaryModel).where(SummaryModel.meeting_id == meeting.meeting_id)
            )
            session.execute(
                delete(ActionItemModel).where(ActionItemModel.meeting_id == meeting.meeting_id)
            )
            session.execute(
                delete(DecisionModel).where(DecisionModel.meeting_id == meeting.meeting_id)
            )
            session.execute(delete(RiskModel).where(RiskModel.meeting_id == meeting.meeting_id))
            session.execute(
                delete(FollowUpModel).where(FollowUpModel.meeting_id == meeting.meeting_id)
            )

            if meeting.summary:
                session.add(
                    SummaryModel(
                        meeting_id=meeting.meeting_id,
                        executive_summary=meeting.summary,
                        topics=[],
                        open_questions=[],
                    )
                )
            session.add_all(self._action_item_rows(meeting))
            session.add_all(self._decision_rows(meeting))
            session.add_all(self._risk_rows(meeting))
            session.add_all(self._follow_up_rows(meeting))
            session.commit()
        return meeting

    async def get(self, meeting_id: UUID) -> MeetingDocument | None:
        from sqlalchemy import select

        from meeting_intel.db.models import (
            ActionItemModel,
            DecisionModel,
            FollowUpModel,
            MeetingModel,
            RiskModel,
            SummaryModel,
        )

        with self.session_factory() as session:
            row = session.get(MeetingModel, meeting_id)
            if row is None:
                return None

            summary = session.scalar(
                select(SummaryModel)
                .where(SummaryModel.meeting_id == meeting_id)
                .order_by(SummaryModel.created_at.desc())
            )
            action_rows = session.scalars(
                select(ActionItemModel).where(ActionItemModel.meeting_id == meeting_id)
            ).all()
            decision_rows = session.scalars(
                select(DecisionModel).where(DecisionModel.meeting_id == meeting_id)
            ).all()
            risk_rows = session.scalars(
                select(RiskModel).where(RiskModel.meeting_id == meeting_id)
            ).all()
            follow_up_rows = session.scalars(
                select(FollowUpModel).where(FollowUpModel.meeting_id == meeting_id)
            ).all()

            return MeetingDocument(
                meeting_id=row.id,
                title=row.title,
                date=row.meeting_date or datetime.now(UTC),
                participants=row.participants,
                transcript=[TranscriptTurn(**turn) for turn in row.transcript],
                summary=summary.executive_summary if summary else "",
                action_items=[self._action_item_from_row(item) for item in action_rows],
                decisions=[self._decision_from_row(item) for item in decision_rows],
                risks=[self._risk_from_row(item) for item in risk_rows],
                follow_ups=[self._follow_up_from_row(item) for item in follow_up_rows],
                source_type=row.source_type,
            )

    def _action_item_rows(self, meeting: MeetingDocument) -> list:
        from meeting_intel.db.models import ActionItemModel

        return [
            ActionItemModel(
                id=item.id,
                meeting_id=meeting.meeting_id,
                description=item.description,
                owner=item.owner,
                due_date=self._parse_date(item.due_date),
                priority=item.priority,
                status=item.status,
                source_quote=item.source_quote,
            )
            for item in meeting.action_items
        ]

    def _decision_rows(self, meeting: MeetingDocument) -> list:
        from meeting_intel.db.models import DecisionModel

        return [
            DecisionModel(
                id=item.id,
                meeting_id=meeting.meeting_id,
                description=item.description,
                owner=item.owner,
                rationale=item.rationale,
                source_quote=item.source_quote,
            )
            for item in meeting.decisions
        ]

    def _risk_rows(self, meeting: MeetingDocument) -> list:
        from meeting_intel.db.models import RiskModel

        return [
            RiskModel(
                id=item.id,
                meeting_id=meeting.meeting_id,
                description=item.description,
                severity=item.severity,
                probability=item.probability,
                mitigation=item.mitigation,
                owner=item.owner,
                status=item.status,
            )
            for item in meeting.risks
        ]

    def _follow_up_rows(self, meeting: MeetingDocument) -> list:
        from meeting_intel.db.models import FollowUpModel

        return [
            FollowUpModel(
                id=item.id,
                meeting_id=meeting.meeting_id,
                recipient=item.recipient,
                subject=item.subject,
                body=item.body,
                tone=item.tone,
            )
            for item in meeting.follow_ups
        ]

    def _action_item_from_row(self, row) -> ActionItem:
        return ActionItem(
            id=row.id,
            description=row.description,
            owner=row.owner,
            due_date=row.due_date.isoformat() if row.due_date else None,
            priority=row.priority,
            status=row.status,
            source_quote=row.source_quote,
        )

    def _decision_from_row(self, row) -> Decision:
        return Decision(
            id=row.id,
            description=row.description,
            owner=row.owner,
            rationale=row.rationale,
            source_quote=row.source_quote,
        )

    def _risk_from_row(self, row) -> Risk:
        return Risk(
            id=row.id,
            description=row.description,
            severity=row.severity,
            probability=row.probability,
            mitigation=row.mitigation,
            owner=row.owner,
            status=row.status,
        )

    def _follow_up_from_row(self, row) -> FollowUp:
        return FollowUp(
            id=row.id,
            recipient=row.recipient,
            subject=row.subject,
            body=row.body,
            tone=row.tone,
        )

    def _parse_date(self, value: str | None) -> date | None:
        if value is None:
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None


repository = InMemoryMeetingRepository()
