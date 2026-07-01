from dataclasses import dataclass

from meeting_intel.schemas import MeetingDocument


@dataclass(frozen=True)
class TextChunk:
    id: str
    meeting_id: str
    text: str
    metadata: dict


def chunk_meeting(
    document: MeetingDocument,
    max_chars: int = 1200,
    overlap: int = 160,
) -> list[TextChunk]:
    if overlap >= max_chars:
        raise ValueError("overlap must be smaller than max_chars")

    transcript = document.transcript_text
    if not transcript:
        return []

    chunks: list[TextChunk] = []
    start = 0
    index = 0
    while start < len(transcript):
        end = min(start + max_chars, len(transcript))
        text = transcript[start:end].strip()
        if text:
            chunks.append(
                TextChunk(
                    id=f"{document.meeting_id}:{index}",
                    meeting_id=str(document.meeting_id),
                    text=text,
                    metadata={
                        "meeting_id": str(document.meeting_id),
                        "title": document.title,
                        "artifact_type": "transcript",
                        "chunk_index": index,
                        "source_type": document.source_type.value,
                        "schema_version": "v1",
                    },
                )
            )
        index += 1
        if end == len(transcript):
            break
        start = max(0, end - overlap)
    return chunks
