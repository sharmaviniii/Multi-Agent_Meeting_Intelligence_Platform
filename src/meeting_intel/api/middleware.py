from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from meeting_intel.observability.logging import get_logger, new_request_id

logger = get_logger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = new_request_id()
        logger.info("request_started", method=request.method, path=request.url.path)
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        logger.info("request_completed", status_code=response.status_code)
        return response
