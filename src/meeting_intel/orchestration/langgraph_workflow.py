from typing import Literal, TypedDict

from langgraph.graph import END, StateGraph

from meeting_intel.rag.vector_store import ChromaMeetingStore, rerank
from meeting_intel.schemas import (
    ActionItem,
    Decision,
    FollowUp,
    MeetingDocument,
    Risk,
    TranscriptTurn,
)
from meeting_intel.services.meeting_intelligence import MeetingIntelligenceService

Intent = Literal["summarization", "action_items", "decisions", "risks", "email_draft"]


class WorkflowResult(TypedDict, total=False):
    answer: str
    sources: list[dict]
    summary: str
    action_items: list[ActionItem]
    decisions: list[Decision]
    risks: list[Risk]
    email: FollowUp


class WorkflowState(TypedDict, total=False):
    question: str
    meeting: MeetingDocument
    meeting_id: str
    top_k: int
    explicit_intent: Intent
    intent: Intent
    hits: list[dict]
    context: str
    result: WorkflowResult
    audience: str
    tone: str
    include_sections: list[str]


class MeetingIntelligenceWorkflow:
    def __init__(
        self,
        store: ChromaMeetingStore,
        intelligence: MeetingIntelligenceService,
    ) -> None:
        self.store = store
        self.intelligence = intelligence
        self.graph = self._build_graph()

    async def run(
        self,
        *,
        question: str,
        top_k: int = 5,
        meeting: MeetingDocument | None = None,
        meeting_id: str | None = None,
        intent: Intent | None = None,
        audience: str = "meeting participants",
        tone: str = "professional",
        include_sections: list[str] | None = None,
    ) -> WorkflowResult:
        state: WorkflowState = {
            "question": question,
            "top_k": top_k,
            "audience": audience,
            "tone": tone,
            "include_sections": include_sections or ["summary", "actions", "decisions", "risks"],
        }
        if meeting is not None:
            state["meeting"] = meeting
            state["meeting_id"] = str(meeting.meeting_id)
        elif meeting_id is not None:
            state["meeting_id"] = meeting_id
        if intent is not None:
            state["explicit_intent"] = intent

        final_state = await self.graph.ainvoke(state)
        return final_state.get("result", {})

    def _build_graph(self):
        graph = StateGraph(WorkflowState)
        graph.add_node("retriever", self._retriever_node)
        graph.add_node("intent_classifier", self._intent_classifier_node)
        graph.add_node("summarization", self._summarization_node)
        graph.add_node("action_items", self._action_items_node)
        graph.add_node("decisions", self._decisions_node)
        graph.add_node("risks", self._risks_node)
        graph.add_node("email_draft", self._email_draft_node)
        graph.add_node("response_formatter", self._response_formatter_node)

        graph.set_entry_point("retriever")
        graph.add_edge("retriever", "intent_classifier")
        graph.add_conditional_edges(
            "intent_classifier",
            self._route_intent,
            {
                "summarization": "summarization",
                "action_items": "action_items",
                "decisions": "decisions",
                "risks": "risks",
                "email_draft": "email_draft",
            },
        )
        for node_name in ("summarization", "action_items", "decisions", "risks", "email_draft"):
            graph.add_edge(node_name, "response_formatter")
        graph.add_edge("response_formatter", END)
        return graph.compile()

    def _retriever_node(self, state: WorkflowState) -> WorkflowState:
        question = state.get("question", "")
        top_k = state.get("top_k", 5)
        search_k = min(top_k * 4, 20)
        if question and "meeting" not in state:
            hits = self.store.search(
                question,
                top_k=search_k,
                meeting_id=state.get("meeting_id"),
                artifact_type="transcript",
            )
            ranked_hits = rerank(question, hits)[:top_k]
        else:
            ranked_hits = []
        return {
            **state,
            "hits": ranked_hits,
            "context": "\n\n".join(hit["text"] for hit in ranked_hits),
        }

    def _intent_classifier_node(self, state: WorkflowState) -> WorkflowState:
        if "explicit_intent" in state:
            return {**state, "intent": state["explicit_intent"]}

        question = state.get("question", "").lower()
        if any(term in question for term in ("email", "follow-up", "follow up", "draft")):
            intent: Intent = "email_draft"
        elif any(term in question for term in ("risk", "blocker", "concern", "issue")):
            intent = "risks"
        elif any(term in question for term in ("decision", "decided", "agreed", "approved")):
            intent = "decisions"
        elif any(term in question for term in ("action", "todo", "to do", "owner", "due")):
            intent = "action_items"
        else:
            intent = "summarization"
        return {**state, "intent": intent}

    def _route_intent(self, state: WorkflowState) -> str:
        return state["intent"]

    async def _summarization_node(self, state: WorkflowState) -> WorkflowState:
        meeting = state.get("meeting")
        if meeting is not None:
            summary = await self.intelligence.summarize(meeting)
            return {**state, "result": {"summary": summary}}

        answer = await self.intelligence.llm.answer(
            "Answer using only the provided meeting context. If context is insufficient, say so.",
            f"Question: {state.get('question', '')}\n\nContext:\n{state.get('context', '')}",
        )
        return {**state, "result": {"answer": answer, "sources": state.get("hits", [])}}

    async def _action_items_node(self, state: WorkflowState) -> WorkflowState:
        action_items = await self.intelligence.extract_action_items(self._meeting_from_state(state))
        return {**state, "result": {"action_items": action_items}}

    async def _decisions_node(self, state: WorkflowState) -> WorkflowState:
        decisions = await self.intelligence.extract_decisions(self._meeting_from_state(state))
        return {**state, "result": {"decisions": decisions}}

    async def _risks_node(self, state: WorkflowState) -> WorkflowState:
        risks = await self.intelligence.extract_risks(self._meeting_from_state(state))
        return {**state, "result": {"risks": risks}}

    async def _email_draft_node(self, state: WorkflowState) -> WorkflowState:
        email = await self.intelligence.draft_follow_up_email(
            self._meeting_from_state(state),
            audience=state.get("audience", "meeting participants"),
            tone=state.get("tone", "professional"),
            include_sections=state.get("include_sections"),
        )
        return {**state, "result": {"email": email}}

    def _response_formatter_node(self, state: WorkflowState) -> WorkflowState:
        result = state.get("result", {})
        if "sources" not in result and state.get("hits"):
            result = {**result, "sources": state["hits"]}
        return {**state, "result": result}

    def _meeting_from_state(self, state: WorkflowState) -> MeetingDocument:
        meeting = state.get("meeting")
        if meeting is not None:
            return meeting
        return MeetingDocument(
            title="Retrieved meeting context",
            transcript=[
                TranscriptTurn(
                    speaker="Context",
                    text=state.get("context") or "No retrieved meeting context was available.",
                )
            ],
        )
