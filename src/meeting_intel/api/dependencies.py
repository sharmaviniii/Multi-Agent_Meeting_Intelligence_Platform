from functools import lru_cache

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from meeting_intel.api.rate_limit import rate_limit_key, rate_limiter
from meeting_intel.core.auth import JWTError, validate_jwt
from meeting_intel.core.config import Settings, get_settings
from meeting_intel.db.repository import (
    InMemoryMeetingRepository,
    MeetingRepository,
    SQLAlchemyMeetingRepository,
)
from meeting_intel.db.session import create_session_factory
from meeting_intel.rag.embeddings import get_embedding_model
from meeting_intel.rag.vector_store import ChromaMeetingStore
from meeting_intel.services.llm import LLMClient
from meeting_intel.services.meeting_intelligence import MeetingIntelligenceService


def settings_dep() -> Settings:
    return get_settings()


bearer_scheme = HTTPBearer(auto_error=False)
BEARER_DEP = Depends(bearer_scheme)
SETTINGS_DEP = Depends(settings_dep)


@lru_cache
def repository_dep() -> MeetingRepository:
    settings = get_settings()
    if settings.offline_mode:
        return InMemoryMeetingRepository()

    session_factory = create_session_factory(settings)
    if session_factory is None:
        return InMemoryMeetingRepository()
    return SQLAlchemyMeetingRepository(session_factory)


@lru_cache
def llm_dep() -> LLMClient:
    return LLMClient(get_settings())


@lru_cache
def intelligence_dep() -> MeetingIntelligenceService:
    settings = get_settings()
    return MeetingIntelligenceService(settings, llm_dep())


@lru_cache
def vector_store_dep() -> ChromaMeetingStore:
    settings = get_settings()
    return ChromaMeetingStore(
        settings,
        get_embedding_model(settings),
    )


async def auth_dep(
    credentials: HTTPAuthorizationCredentials | None = None,
    settings: Settings | None = None,
) -> dict:
    settings = settings or get_settings()
    if settings.offline_mode:
        return {"sub": "offline-local", "offline": True}
    if not settings.jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="JWT authentication is not configured",
        )
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return validate_jwt(credentials.credentials, settings.jwt_secret, settings.jwt_issuer)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def current_user_dep(
    credentials: HTTPAuthorizationCredentials | None = BEARER_DEP,
    settings: Settings = SETTINGS_DEP,
) -> dict:
    return await auth_dep(credentials, settings)


async def rate_limit_dep(
    request: Request,
    settings: Settings = SETTINGS_DEP,
) -> None:
    rate_limiter.check(rate_limit_key(request), settings)
