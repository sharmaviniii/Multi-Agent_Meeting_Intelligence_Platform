from meeting_intel.ingestion.meetingbank import load_meetingbank
from meeting_intel.ingestion.parsers import normalize_meetingbank_record, parse_transcript_text
from meeting_intel.schemas import SourceType


def test_parse_transcript_text_normalizes_speakers():
    meeting = parse_transcript_text(
        "ASHA: We need the launch plan.\nRahul: I will own the API.",
        title="Launch Sync",
    )

    assert meeting.title == "Launch Sync"
    assert meeting.participants == ["Asha", "Rahul"]
    assert meeting.transcript[0].speaker == "Asha"
    assert meeting.transcript[1].text == "I will own the API."


def test_normalize_meetingbank_record_maps_common_fields():
    meeting = normalize_meetingbank_record(
        {
            "id": "abc",
            "title": "Council Meeting",
            "transcript": "Chair: Budget review starts now.",
            "summary": "Budget was reviewed.",
        }
    )

    assert meeting.source_type == SourceType.meetingbank
    assert meeting.summary == "Budget was reviewed."
    assert meeting.embeddings_metadata["source_record_id"] == "abc"


def test_load_meetingbank_jsonl(tmp_path):
    path = tmp_path / "meetingbank.jsonl"
    path.write_text(
        '{"id":"1","title":"One","transcript":"A: Hello","summary":"Greeting"}\n'
        '{"id":"2","title":"Two","transcript":"B: Bye","summary":"Closing"}\n',
        encoding="utf-8",
    )

    meetings = load_meetingbank(path)

    assert len(meetings) == 2
    assert meetings[0].title == "One"
    assert meetings[1].summary == "Closing"
