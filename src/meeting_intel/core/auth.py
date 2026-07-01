import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta
from typing import Any


class JWTError(Exception):
    pass


def create_jwt(
    subject: str,
    secret: str,
    issuer: str = "meeting-intelligence",
    expires_delta: timedelta | None = None,
    now: datetime | None = None,
) -> str:
    issued_at = now or datetime.now(UTC)
    expires_at = issued_at + (expires_delta or timedelta(minutes=60))
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": subject,
        "iss": issuer,
        "iat": int(issued_at.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    signing_input = f"{_encode_json(header)}.{_encode_json(payload)}"
    signature = _sign(signing_input, secret)
    return f"{signing_input}.{signature}"


def validate_jwt(
    token: str,
    secret: str,
    issuer: str = "meeting-intelligence",
    now: datetime | None = None,
) -> dict[str, Any]:
    parts = token.split(".")
    if len(parts) != 3:
        raise JWTError("Invalid token format")

    signing_input = f"{parts[0]}.{parts[1]}"
    expected_signature = _sign(signing_input, secret)
    if not hmac.compare_digest(expected_signature, parts[2]):
        raise JWTError("Invalid token signature")

    payload = _decode_json(parts[1])
    if payload.get("iss") != issuer:
        raise JWTError("Invalid token issuer")

    expires_at = payload.get("exp")
    if not isinstance(expires_at, int):
        raise JWTError("Token expiration is required")

    current_time = now or datetime.now(UTC)
    if current_time.timestamp() >= expires_at:
        raise JWTError("Token has expired")

    if not payload.get("sub"):
        raise JWTError("Token subject is required")

    return payload


def _encode_json(value: dict[str, Any]) -> str:
    raw = json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return _base64url_encode(raw)


def _decode_json(value: str) -> dict[str, Any]:
    try:
        raw = _base64url_decode(value)
        decoded = json.loads(raw)
    except (ValueError, json.JSONDecodeError) as exc:
        raise JWTError("Invalid token payload") from exc
    if not isinstance(decoded, dict):
        raise JWTError("Invalid token payload")
    return decoded


def _sign(signing_input: str, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256)
    return _base64url_encode(digest.digest())


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}")
