import pytest

from meeting_intel.api.dependencies import repository_dep
from meeting_intel.core.config import Settings, get_settings
from meeting_intel.db.repository import InMemoryMeetingRepository
from meeting_intel.db.session import create_session_factory
from meeting_intel.ingestion.parsers import parse_transcript_text


@pytest.mark.asyncio
async def test_in_memory_repository_saves_and_gets_meeting():
    repo = InMemoryMeetingRepository()
    meeting = parse_transcript_text("Asha: We need the demo.", title="Repo Demo")

    await repo.save(meeting)
    loaded = await repo.get(meeting.meeting_id)

    assert loaded == meeting


def test_repository_dependency_uses_in_memory_when_offline(monkeypatch):
    monkeypatch.setenv("OFFLINE_MODE", "true")
    get_settings.cache_clear()
    repository_dep.cache_clear()

    try:
        repo = repository_dep()
    finally:
        get_settings.cache_clear()
        repository_dep.cache_clear()

    assert isinstance(repo, InMemoryMeetingRepository)


def test_session_factory_requires_database_url_when_online():
    settings = Settings(offline_mode=False, database_url=None)

    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        create_session_factory(settings)
