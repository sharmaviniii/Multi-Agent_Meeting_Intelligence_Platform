from datetime import UTC, datetime, timedelta

import pytest

from meeting_intel.core.auth import JWTError, create_jwt, validate_jwt


def test_create_and_validate_jwt_with_expiration_claim():
    now = datetime(2026, 1, 1, tzinfo=UTC)
    token = create_jwt(
        "user-123",
        "secret",
        issuer="tests",
        expires_delta=timedelta(minutes=5),
        now=now,
    )

    payload = validate_jwt(token, "secret", issuer="tests", now=now + timedelta(minutes=1))

    assert payload["sub"] == "user-123"
    assert "exp" in payload


def test_validate_jwt_rejects_expired_token():
    now = datetime(2026, 1, 1, tzinfo=UTC)
    token = create_jwt(
        "user-123",
        "secret",
        issuer="tests",
        expires_delta=timedelta(seconds=1),
        now=now,
    )

    with pytest.raises(JWTError, match="expired"):
        validate_jwt(token, "secret", issuer="tests", now=now + timedelta(seconds=2))


def test_validate_jwt_rejects_invalid_signature():
    token = create_jwt("user-123", "secret", issuer="tests")

    with pytest.raises(JWTError, match="signature"):
        validate_jwt(token, "different-secret", issuer="tests")
