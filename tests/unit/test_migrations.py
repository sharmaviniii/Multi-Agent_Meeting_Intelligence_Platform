from pathlib import Path

MIGRATION_PATH = (
    Path(__file__).parents[2]
    / "alembic"
    / "versions"
    / "20260627_0001_initial_persistence_schema.py"
)


def test_initial_migration_file_exists():
    assert MIGRATION_PATH.exists()


def test_initial_migration_covers_persistence_tables():
    migration = MIGRATION_PATH.read_text(encoding="utf-8")

    for table_name in [
        "users",
        "meetings",
        "summaries",
        "action_items",
        "decisions",
        "risks",
        "follow_ups",
        "embedding_metadata",
        "conversation_history",
    ]:
        assert f'"{table_name}"' in migration


def test_initial_migration_defines_expected_indexes():
    migration = MIGRATION_PATH.read_text(encoding="utf-8")

    for index_name in [
        "idx_meetings_created_at",
        "idx_meetings_source_type",
        "idx_action_items_meeting_id",
        "idx_decisions_meeting_id",
        "idx_risks_meeting_id",
        "idx_embedding_metadata_meeting_id",
        "idx_embedding_metadata_artifact_type",
        "idx_conversation_history_conversation_id",
    ]:
        assert index_name in migration
