from uuid import UUID

from meeting_intel.schemas import MeetingDocument


class InMemoryMeetingRepository:
    def __init__(self) -> None:
        self._meetings: dict[UUID, MeetingDocument] = {}

    async def save(self, meeting: MeetingDocument) -> MeetingDocument:
        self._meetings[meeting.meeting_id] = meeting
        return meeting

    async def get(self, meeting_id: UUID) -> MeetingDocument | None:
        return self._meetings.get(meeting_id)


repository = InMemoryMeetingRepository()
