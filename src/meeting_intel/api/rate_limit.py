from dataclasses import dataclass
from time import monotonic

from fastapi import HTTPException, Request, status

from meeting_intel.core.config import Settings


@dataclass
class RateLimitBucket:
    count: int
    window_started_at: float


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._buckets: dict[str, RateLimitBucket] = {}

    def check(self, key: str, settings: Settings) -> None:
        now = monotonic()
        window = settings.rate_limit_window_seconds
        bucket = self._buckets.get(key)
        if bucket is None or now - bucket.window_started_at >= window:
            self._buckets[key] = RateLimitBucket(count=1, window_started_at=now)
            return

        bucket.count += 1
        if bucket.count > settings.rate_limit_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )

    def clear(self) -> None:
        self._buckets.clear()


rate_limiter = InMemoryRateLimiter()


def rate_limit_key(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        client_host = forwarded_for.split(",", 1)[0].strip()
    elif request.client:
        client_host = request.client.host
    else:
        client_host = "unknown"
    return f"{request.url.path}:{client_host}"
