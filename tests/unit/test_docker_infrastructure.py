from pathlib import Path

ROOT = Path(__file__).parents[2]


def test_dockerfile_runs_fastapi_app():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "python:3.11-slim" in dockerfile
    assert "pip install --no-cache-dir ." in dockerfile
    assert "meeting_intel.api.app:app" in dockerfile


def test_compose_defines_api_postgres_and_chroma_persistence():
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert "api:" in compose
    assert "postgres:" in compose
    assert "chroma_data:" in compose
    assert "postgres:16-alpine" in compose


def test_compose_preserves_offline_default_and_persistence_settings():
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert "OFFLINE_MODE: ${OFFLINE_MODE:-true}" in compose
    assert "DATABASE_URL:" in compose
    assert "postgresql+psycopg://meeting_intel:meeting_intel@postgres:5432/meeting_intel" in compose
    assert "CHROMA_PATH: ${CHROMA_PATH:-/app/chroma}" in compose
    assert "chroma_data:/app/chroma" in compose
    assert "chroma_data:" in compose
