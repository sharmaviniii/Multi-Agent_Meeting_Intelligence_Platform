from functools import lru_cache

from meeting_intel.core.config import Settings, get_settings
from meeting_intel.db.repository import InMemoryMeetingRepository, repository
from meeting_intel.rag.embeddings import get_embedding_model
from meeting_intel.rag.vector_store import ChromaMeetingStore
from meeting_intel.services.llm import LLMClient
from meeting_intel.services.meeting_intelligence import MeetingIntelligenceService


def settings_dep() -> Settings:
    return get_settings()


def repository_dep() -> InMemoryMeetingRepository:
    return repository


@lru_cache
def llm_dep() -> LLMClient:
    return LLMClient(get_settings())


@lru_cache
def intelligence_dep() -> MeetingIntelligenceService:
    settings = get_settings()
    return MeetingIntelligenceService(settings, llm_dep())


@lru_cache
def vector_store_dep() -> ChromaMeetingStore:
    settings = get_settings()
    return ChromaMeetingStore(
        settings,
        get_embedding_model(settings.embedding_model, offline_mode=settings.offline_mode),
    )
