from meeting_intel.core.config import Settings
from meeting_intel.schemas import ActionItem, Decision, FollowUp, MeetingDocument, Risk
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

    async def extract_action_items(self, meeting: MeetingDocument) -> list[ActionItem]:
        if self.settings.offline_mode or self.llm.client is None:
            return self._offline_action_items(meeting)

        payload = await self.llm.complete_json(
            "Extract meeting action items with owner, due date, priority, and source quote.",
            meeting.transcript_text,
            '{"action_items": [{"description": "string", "owner": "string|null", '
            '"due_date": "string|null", "priority": "low|medium|high", '
            '"source_quote": "string|null"}]}',
        )
        return [ActionItem(**item) for item in payload.get("action_items", [])]

    async def extract_decisions(self, meeting: MeetingDocument) -> list[Decision]:
        if self.settings.offline_mode or self.llm.client is None:
            return self._offline_decisions(meeting)

        payload = await self.llm.complete_json(
            "Extract decisions made in the meeting with owner, rationale, and source quote.",
            meeting.transcript_text,
            '{"decisions": [{"description": "string", "owner": "string|null", '
            '"rationale": "string|null", "source_quote": "string|null"}]}',
        )
        return [Decision(**item) for item in payload.get("decisions", [])]

    async def extract_risks(self, meeting: MeetingDocument) -> list[Risk]:
        if self.settings.offline_mode or self.llm.client is None:
            return self._offline_risks(meeting)

        payload = await self.llm.complete_json(
            "Extract meeting risks with severity, probability, mitigation, owner, "
            "and source quote.",
            meeting.transcript_text,
            '{"risks": [{"description": "string", "severity": "low|medium|high", '
            '"probability": "low|medium|high", "mitigation": "string|null", '
            '"owner": "string|null"}]}',
        )
        return [Risk(**item) for item in payload.get("risks", [])]

    async def draft_follow_up_email(
        self,
        meeting: MeetingDocument,
        audience: str = "meeting participants",
        tone: str = "professional",
        include_sections: list[str] | None = None,
    ) -> FollowUp:
        sections = include_sections or ["summary", "actions", "decisions", "risks"]
        if self.settings.offline_mode or self.llm.client is None:
            return self._offline_email(meeting, audience, tone, sections)

        payload = await self.llm.complete_json(
            "Draft a follow-up email from meeting intelligence.",
            self._email_context(meeting, audience, tone, sections),
            '{"recipient": "string", "subject": "string", "body": "string"}',
        )
        return FollowUp(
            recipient=str(payload.get("recipient") or audience),
            subject=str(payload.get("subject") or f"Follow-up: {meeting.title}"),
            body=str(payload.get("body") or ""),
            tone=tone,
        )

    def generate_heuristic_summary(self, meeting: MeetingDocument) -> str:
        participants = ", ".join(meeting.participants[:6]) or "the meeting participants"
        themes = self._keyword_themes(meeting)
        first_turns = " ".join(turn.text for turn in meeting.transcript[:3])
        preview = " ".join(first_turns.split())[:300]
        theme_text = f" Key themes: {', '.join(themes)}." if themes else ""
        return (
            f"{meeting.title} included discussion among {participants}. "
            f"{preview or 'The transcript was captured for review.'}{theme_text}"
        )

    def generate_heuristic_analysis(self, meeting: MeetingDocument) -> None:
        meeting.summary = self.generate_heuristic_summary(meeting)
        meeting.action_items = self._offline_action_items(meeting)
        meeting.decisions = self._offline_decisions(meeting)
        meeting.risks = self._offline_risks(meeting)
        meeting.follow_ups = [
            self._offline_email(
                meeting,
                audience="meeting participants",
                tone="professional",
                include_sections=["summary", "actions", "decisions", "risks"],
            )
        ]

    def _offline_action_items(self, meeting: MeetingDocument) -> list[ActionItem]:
        action_items = []
        cues = (" will ", " need to ", " needs to ", " should ", " by ")
        for turn in meeting.transcript:
            lowered = f" {turn.text.lower()} "
            if any(cue in lowered for cue in cues):
                action_items.append(
                    ActionItem(
                        description=turn.text,
                        owner=turn.speaker if turn.speaker != "Unknown" else None,
                        due_date="Friday" if "friday" in lowered else None,
                        priority="high" if "must" in lowered or "urgent" in lowered else "medium",
                        source_quote=f"{turn.speaker}: {turn.text}",
                    )
                )
        return action_items

    def _offline_decisions(self, meeting: MeetingDocument) -> list[Decision]:
        decisions = []
        cues = ("decided", "decision", "agreed", "approved", "let's", "we will")
        for turn in meeting.transcript:
            lowered = turn.text.lower()
            if any(cue in lowered for cue in cues):
                decisions.append(
                    Decision(
                        description=turn.text,
                        owner=turn.speaker if turn.speaker != "Unknown" else None,
                        rationale="Offline extraction identified decision-oriented language.",
                        source_quote=f"{turn.speaker}: {turn.text}",
                    )
                )
        return decisions

    def _offline_risks(self, meeting: MeetingDocument) -> list[Risk]:
        risks = []
        cues = ("risk", "blocked", "blocker", "concern", "delay", "issue", "problem")
        for turn in meeting.transcript:
            lowered = turn.text.lower()
            if any(cue in lowered for cue in cues):
                risks.append(
                    Risk(
                        description=turn.text,
                        severity=(
                            "high"
                            if "blocked" in lowered or "blocker" in lowered
                            else "medium"
                        ),
                        probability="medium",
                        mitigation="Review owner, timeline, and fallback plan.",
                        owner=turn.speaker if turn.speaker != "Unknown" else None,
                    )
                )
        return risks

    def _offline_email(
        self,
        meeting: MeetingDocument,
        audience: str,
        tone: str,
        include_sections: list[str],
    ) -> FollowUp:
        lines = [f"Hi {audience},", "", f"Here is the follow-up for {meeting.title}."]
        if "summary" in include_sections and meeting.summary:
            lines.extend(["", f"Summary: {meeting.summary}"])
        if "actions" in include_sections and meeting.action_items:
            lines.extend(["", "Action items:"])
            lines.extend(f"- {item.description}" for item in meeting.action_items)
        if "decisions" in include_sections and meeting.decisions:
            lines.extend(["", "Decisions:"])
            lines.extend(f"- {decision.description}" for decision in meeting.decisions)
        if "risks" in include_sections and meeting.risks:
            lines.extend(["", "Risks:"])
            lines.extend(f"- {risk.description}" for risk in meeting.risks)
        lines.extend(["", "Thanks,"])
        return FollowUp(
            recipient=audience,
            subject=f"Follow-up: {meeting.title}",
            body="\n".join(lines),
            tone=tone,
        )

    def _keyword_themes(self, meeting: MeetingDocument) -> list[str]:
        stop_words = {
            "about",
            "after",
            "again",
            "also",
            "because",
            "before",
            "could",
            "from",
            "have",
            "meeting",
            "need",
            "should",
            "that",
            "their",
            "there",
            "this",
            "will",
            "with",
            "would",
        }
        counts: dict[str, int] = {}
        for word in meeting.transcript_text.lower().replace(":", " ").split():
            normalized = "".join(character for character in word if character.isalnum())
            if len(normalized) < 4 or normalized in stop_words:
                continue
            counts[normalized] = counts.get(normalized, 0) + 1
        return [
            word
            for word, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:5]
        ]

    def _email_context(
        self,
        meeting: MeetingDocument,
        audience: str,
        tone: str,
        include_sections: list[str],
    ) -> str:
        return (
            f"Meeting: {meeting.title}\n"
            f"Audience: {audience}\n"
            f"Tone: {tone}\n"
            f"Sections: {', '.join(include_sections)}\n"
            f"Summary: {meeting.summary}\n"
            f"Action items: {[item.model_dump(mode='json') for item in meeting.action_items]}\n"
            f"Decisions: {[item.model_dump(mode='json') for item in meeting.decisions]}\n"
            f"Risks: {[item.model_dump(mode='json') for item in meeting.risks]}"
        )
