from meeting_intel.ingestion.parsers import parse_transcript_text
from meeting_intel.rag.chunking import chunk_meeting


def test_chunk_meeting_adds_metadata():
    meeting = parse_transcript_text(
        "Asha: " + "alpha beta gamma " * 50,
        title="Chunk Demo",
    )

    chunks = chunk_meeting(meeting, max_chars=120, overlap=20)

    assert len(chunks) > 1
    assert chunks[0].metadata["artifact_type"] == "transcript"
    assert chunks[0].metadata["title"] == "Chunk Demo"


def test_chunk_meeting_rejects_invalid_overlap():
    meeting = parse_transcript_text("Asha: hello", title="Bad Chunk")

    try:
        chunk_meeting(meeting, max_chars=100, overlap=100)
    except ValueError as exc:
        assert "overlap" in str(exc)
    else:
        raise AssertionError("Expected invalid overlap to raise ValueError")
