from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
        description=(
    "FastAPI, MeetingBank ingestion, "
    "ChromaDB retrieval, and GPT-4o-mini summarization."),   )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )
    app.add_middleware(RequestContextMiddleware)
    install_exception_handlers(app)
    app.include_router(router)
    return app


app = create_app()
