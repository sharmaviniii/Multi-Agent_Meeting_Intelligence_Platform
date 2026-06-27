from meeting_intel.core.config import Settings
from meeting_intel.schemas import MeetingDocument
from meeting_intel.services.llm import LLMClient


class MeetingIntelligenceService:
    def __init__(self, settings: Settings, llm: LLMClient) -> None:
        self.settings = settings
        self.llm = llm

    async def summarize(self, meeting: MeetingDocument) -> str:
        if len(meeting.transcript_text) > self.settings.max_transcript_chars_for_direct_summary:
            return await self.map_reduce_summary(meeting)

        payload = await self.llm.complete_json(
            "You summarize meeting transcripts for enterprise teams. Return a concise summary.",
            meeting.transcript_text,
            '{"summary": "string"}',
        )
        return str(payload.get("summary", ""))

    async def map_reduce_summary(self, meeting: MeetingDocument) -> str:
        from meeting_intel.rag.chunking import chunk_meeting

        partials = []
        chunks = chunk_meeting(
            meeting,
            max_chars=min(6000, self.settings.max_transcript_chars_for_direct_summary),
            overlap=200,
        )
        for chunk in chunks:
            payload = await self.llm.complete_json(
                "Summarize this transcript chunk with key topics, outcomes, and open questions.",
                chunk.text,
                '{"summary": "string"}',
            )
            partials.append(str(payload.get("summary", "")))

        final = await self.llm.complete_json(
            "Combine chunk summaries into one executive meeting summary.",
            "\n".join(partials),
            '{"summary": "string"}',
        )
        return str(final.get("summary", ""))
