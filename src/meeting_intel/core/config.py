import os
from dataclasses import dataclass
from functools import lru_cache


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "local")
    offline_mode: bool = _bool_env("OFFLINE_MODE", True)
    service_name: str = os.getenv("SERVICE_NAME", "meeting-intelligence-api")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY") or None
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    chroma_host: str = os.getenv("CHROMA_HOST", "localhost")
    chroma_port: int = _int_env("CHROMA_PORT", 8000)
    chroma_collection: str = os.getenv("CHROMA_COLLECTION", "meeting_memory")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    max_transcript_chars_for_direct_summary: int = _int_env(
        "MAX_TRANSCRIPT_CHARS_FOR_DIRECT_SUMMARY", 16000
    )
    chunk_max_chars: int = _int_env("CHUNK_MAX_CHARS", 1200)
    chunk_overlap_chars: int = _int_env("CHUNK_OVERLAP_CHARS", 160)
    meetingbank_url: str | None = os.getenv("MEETINGBANK_URL") or None
    data_dir: str = os.getenv("DATA_DIR", "data")


@lru_cache
def get_settings() -> Settings:
    return Settings()
