from time import perf_counter

from fastapi import Request
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware

from meeting_intel.observability.logging import get_logger, new_request_id, set_request_id

logger = get_logger(__name__)
REQUEST_COUNT = Counter(
    "meeting_intel_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)
REQUEST_LATENCY = Histogram(
    "meeting_intel_http_request_latency_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id")
        if request_id:
            set_request_id(request_id)
        else:
            request_id = new_request_id()
        start = perf_counter()
        method = request.method
        path = request.url.path
        logger.info("request_started", method=method, path=path)
        response = await call_next(request)
        latency_ms = round((perf_counter() - start) * 1000, 3)
        response.headers["x-request-id"] = request_id
        REQUEST_COUNT.labels(method=method, path=path, status_code=str(response.status_code)).inc()
        REQUEST_LATENCY.labels(method=method, path=path).observe(latency_ms / 1000)
        logger.info(
            "request_completed",
            method=method,
            path=path,
            status_code=response.status_code,
            latency_ms=latency_ms,
        )
        return response
