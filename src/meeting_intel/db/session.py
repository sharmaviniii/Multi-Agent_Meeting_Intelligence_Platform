from collections.abc import Generator

from meeting_intel.core.config import Settings, get_settings


def create_session_factory(settings: Settings | None = None):
    settings = settings or get_settings()
    if settings.offline_mode:
        return None
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is required when OFFLINE_MODE=false")

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(settings.database_url, pool_pre_ping=True)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db_session() -> Generator:
    session_factory = create_session_factory()
    if session_factory is None:
        return

    session = session_factory()
    try:
        yield session
    finally:
        session.close()
