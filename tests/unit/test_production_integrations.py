from pathlib import Path

from meeting_intel.core.config import Settings
from meeting_intel.rag.embeddings import (
    LocalEmbeddingModel,
    MockEmbeddingModel,
    get_embedding_model,
)
from meeting_intel.services.llm import LLMClient


def test_production_embedding_dependencies_are_declared():
    dependencies = Path("pyproject.toml").read_text(encoding="utf-8")

    assert '"sentence-transformers>=5.0.0"' in dependencies
    assert '"torch>=2.8.0"' in dependencies


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
    model = get_embedding_model("BAAI/bge-small-en-v1.5", offline_mode=True)

    assert isinstance(model, MockEmbeddingModel)
    assert model.model_name == "mock-embedding"


def test_embedding_factory_uses_bge_model_in_production_mode():
    model = get_embedding_model("BAAI/bge-small-en-v1.5", offline_mode=False)

    assert isinstance(model, LocalEmbeddingModel)
    assert model.model_name == "BAAI/bge-small-en-v1.5"
