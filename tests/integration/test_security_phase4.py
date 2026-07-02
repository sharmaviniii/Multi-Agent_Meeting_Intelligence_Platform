from datetime import timedelta

from fastapi.testclient import TestClient

from meeting_intel.api.app import create_app
from meeting_intel.api.dependencies import repository_dep, settings_dep, vector_store_dep
from meeting_intel.api.rate_limit import rate_limiter
from meeting_intel.core.auth import create_jwt
from meeting_intel.core.config import Settings, get_settings
from meeting_intel.db.repository import InMemoryMeetingRepository


class NoopVectorStore:
    def upsert_chunks(self, chunks):
        return None

    def search(self, query, top_k=5, meeting_id=None, artifact_type=None):
        return []


def test_public_endpoint_accepts_missing_token_in_production():
    app = create_app()
    app.dependency_overrides[settings_dep] = lambda: Settings(
        offline_mode=False,
        jwt_secret="test-secret",
        database_url="postgresql+psycopg://unused",
    )
    app.dependency_overrides[repository_dep] = lambda: InMemoryMeetingRepository()
    app.dependency_overrides[vector_store_dep] = lambda: NoopVectorStore()

    response = TestClient(app).post(
        "/upload",
        json={"title": "Secure", "text": "Asha: Hello"},
    )

    assert response.status_code == 200


def test_public_endpoint_accepts_valid_token_in_production():
    app = create_app()
    repo = InMemoryMeetingRepository()
    app.dependency_overrides[settings_dep] = lambda: Settings(
        offline_mode=False,
        jwt_secret="test-secret",
        database_url="postgresql+psycopg://unused",
    )
    app.dependency_overrides[repository_dep] = lambda: repo
    app.dependency_overrides[vector_store_dep] = lambda: NoopVectorStore()
    token = create_jwt("user-123", "test-secret")

    response = TestClient(app).post(
        "/upload",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Secure", "text": "Asha: Hello"},
    )

    assert response.status_code == 200
    assert response.json()["meeting"]["title"] == "Secure"


def test_public_endpoint_accepts_invalid_token_in_production():
    app = create_app()
    app.dependency_overrides[settings_dep] = lambda: Settings(
        offline_mode=False,
        jwt_secret="test-secret",
        database_url="postgresql+psycopg://unused",
    )
    app.dependency_overrides[repository_dep] = lambda: InMemoryMeetingRepository()
    app.dependency_overrides[vector_store_dep] = lambda: NoopVectorStore()

    response = TestClient(app).post(
        "/upload",
        headers={"Authorization": "Bearer invalid-token"},
        json={"title": "Secure", "text": "Asha: Hello"},
    )

    assert response.status_code == 200


def test_public_endpoint_accepts_expired_token_in_production():
    app = create_app()
    app.dependency_overrides[settings_dep] = lambda: Settings(
        offline_mode=False,
        jwt_secret="test-secret",
        database_url="postgresql+psycopg://unused",
    )
    app.dependency_overrides[repository_dep] = lambda: InMemoryMeetingRepository()
    app.dependency_overrides[vector_store_dep] = lambda: NoopVectorStore()
    token = create_jwt("user-123", "test-secret", expires_delta=timedelta(seconds=-1))

    response = TestClient(app).post(
        "/upload",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Secure", "text": "Asha: Hello"},
    )

    assert response.status_code == 200


def test_rate_limiter_rejects_requests_after_limit():
    rate_limiter.clear()
    app = create_app()
    app.dependency_overrides[settings_dep] = lambda: Settings(
        offline_mode=True,
        rate_limit_requests=1,
        rate_limit_window_seconds=60,
    )

    client = TestClient(app)
    first_response = client.post("/ask", json={"question": "Anything?", "top_k": 1})
    second_response = client.post("/ask", json={"question": "Anything?", "top_k": 1})

    assert first_response.status_code == 200
    assert second_response.status_code == 429


def test_health_ready_live_and_metrics_are_public():
    get_settings.cache_clear()
    app = create_app()
    client = TestClient(app)

    assert client.get("/health").status_code == 200
    assert client.get("/ready").status_code == 200
    assert client.get("/live").status_code == 200
    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200
    assert "meeting_intel_http_requests_total" in metrics_response.text
