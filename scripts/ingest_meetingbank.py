from meeting_intel.core.config import get_settings
from meeting_intel.ingestion.meetingbank import ingest_meetingbank


def main() -> None:
    settings = get_settings()
    meetings = ingest_meetingbank(settings)
    print(f"Ingested {len(meetings)} MeetingBank records")
    for meeting in meetings[:5]:
        print(f"- {meeting.title}: {len(meeting.transcript)} turns")


if __name__ == "__main__":
    main()
