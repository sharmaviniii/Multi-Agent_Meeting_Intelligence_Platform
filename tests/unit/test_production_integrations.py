from pathlib import Path

from meeting_intel.core.config import Settings
from meeting_intel.rag.embeddings import (
    MockEmbeddingModel,
    OpenAIEmbeddingModel,
    get_embedding_model,
)
from meeting_intel.services.llm import LLMClient


def test_production_embedding_dependencies_are_declared():
    dependencies = Path("pyproject.toml").read_text(encoding="utf-8")

    assert '"openai>=1.40.0"' in dependencies
    assert "sentence-transformers" not in dependencies
    assert '"torch' not in dependencies


def test_llm_client_stays_offline_without_credentials():
    settings = Settings(offline_mode=True, openai_api_key="test-key")

    client = LLMClient(settings)

    assert client.client is None
    assert client.production_enabled is False


def test_llm_client_requires_openai_key_for_production():
    settings = Settings(offline_mode=False, openai_api_key=None)

    client = LLMClient(settings)

    assert client.client is None
    assert client.production_enabled is False


def test_embedding_factory_preserves_offline_mock_mode():
    settings = Settings(offline_mode=True, openai_api_key="test-key")

    model = get_embedding_model(settings)

    assert isinstance(model, MockEmbeddingModel)
    assert model.model_name == "mock-embedding"


def test_embedding_factory_uses_openai_model_in_production_mode():
    settings = Settings(
        offline_mode=False,
        openai_api_key="test-key",
        embedding_model="text-embedding-3-small",
    )

    model = get_embedding_model(settings)

    assert isinstance(model, OpenAIEmbeddingModel)
    assert model.model_name == "text-embedding-3-small"


def test_embedding_factory_requires_openai_key_in_production_mode():
    settings = Settings(offline_mode=False, openai_api_key=None)

    try:
        get_embedding_model(settings)
    except RuntimeError as exc:
        assert "OPENAI_API_KEY" in str(exc)
    else:
        raise AssertionError("Expected production embeddings to require OPENAI_API_KEY")
