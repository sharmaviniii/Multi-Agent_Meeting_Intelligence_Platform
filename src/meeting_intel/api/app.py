from fastapi import FastAPI

from meeting_intel.api.errors import install_exception_handlers
from meeting_intel.api.middleware import RequestContextMiddleware
from meeting_intel.api.routes import router
from meeting_intel.core.config import get_settings
from meeting_intel.observability.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    app = FastAPI(
        title="Meeting Intelligence Phase 1 API",
        version="0.1.0",
        description="FastAPI, MeetingBank ingestion, ChromaDB retrieval, and GPT-4o-mini summarization.",
    )
    app.add_middleware(RequestContextMiddleware)
    install_exception_handlers(app)
    app.include_router(router)
    return app


app = create_app()
