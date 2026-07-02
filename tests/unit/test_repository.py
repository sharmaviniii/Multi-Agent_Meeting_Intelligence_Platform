import pytest

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from meeting_intel.api.dependencies import repository_dep
from meeting_intel.core.config import Settings, get_settings
from meeting_intel.db.models import Base
from meeting_intel.db.repository import InMemoryMeetingRepository, SQLAlchemyMeetingRepository
from meeting_intel.db.session import create_session_factory
from meeting_intel.ingestion.parsers import parse_transcript_text
from meeting_intel.schemas import ActionItem, Decision, FollowUp, Risk


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


@pytest.mark.asyncio
async def test_sqlalchemy_repository_persists_meeting_aggregate_without_fk_violation(tmp_path):
    db_path = tmp_path / 'test_repository.db'
    engine = create_engine(f'sqlite:///{db_path}', future=True)
    Base.metadata.create_all(engine)
    SessionFactory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    repo = SQLAlchemyMeetingRepository(SessionFactory)

    meeting = parse_transcript_text(
        "Asha: We need the demo ready by Friday.\nRahul: I will finish the API.",
        title="Repo Demo",
    )
    meeting.action_items = [ActionItem(description="Finish API", owner="Rahul")]
    meeting.decisions = [Decision(description="Ship on Friday", owner="Asha")]
    meeting.risks = [Risk(description="Vendor delay", severity="medium")]
    meeting.follow_ups = [FollowUp(subject="Follow-up", body="Will do.")]

    await repo.save(meeting)
    loaded = await repo.get(meeting.meeting_id)

    assert loaded is not None
    assert loaded.meeting_id == meeting.meeting_id
    assert loaded.action_items[0].description == "Finish API"
    assert loaded.decisions[0].description == "Ship on Friday"
    assert loaded.risks[0].description == "Vendor delay"
    assert loaded.follow_ups[0].subject == "Follow-up"


@pytest.mark.asyncio
async def test_sqlalchemy_repository_inserts_parent_before_children(tmp_path):
    db_path = tmp_path / 'test_ordering.db'
    engine = create_engine(f'sqlite:///{db_path}', future=True)
    Base.metadata.create_all(engine)
    SessionFactory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    repo = SQLAlchemyMeetingRepository(SessionFactory)

    statements: list[str] = []

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement.strip().lower())

    event.listen(engine, 'before_cursor_execute', before_cursor_execute)

    meeting = parse_transcript_text(
        "Asha: We need the demo ready by Friday.\nRahul: I will finish the API.",
        title="Order Demo",
    )
    meeting.action_items = [ActionItem(description="Finish API", owner="Rahul")]
    meeting.decisions = [Decision(description="Ship on Friday", owner="Asha")]
    meeting.risks = [Risk(description="Vendor delay", severity="medium")]
    meeting.follow_ups = [FollowUp(subject="Follow-up", body="Will do.")]

    await repo.save(meeting)

    event.remove(engine, 'before_cursor_execute', before_cursor_execute)

    assert any('insert into meetings' in stmt for stmt in statements)
    assert any('insert into action_items' in stmt for stmt in statements)
    assert any('insert into decisions' in stmt for stmt in statements)
    assert any('insert into risks' in stmt for stmt in statements)
    assert any('insert into follow_ups' in stmt for stmt in statements)
    assert statements.index(next(stmt for stmt in statements if 'insert into meetings' in stmt)) < statements.index(
        next(stmt for stmt in statements if 'insert into action_items' in stmt)
    )
    assert statements.index(next(stmt for stmt in statements if 'insert into meetings' in stmt)) < statements.index(
        next(stmt for stmt in statements if 'insert into decisions' in stmt)
    )
    assert statements.index(next(stmt for stmt in statements if 'insert into meetings' in stmt)) < statements.index(
        next(stmt for stmt in statements if 'insert into risks' in stmt)
    )
    assert statements.index(next(stmt for stmt in statements if 'insert into meetings' in stmt)) < statements.index(
        next(stmt for stmt in statements if 'insert into follow_ups' in stmt)
    )
