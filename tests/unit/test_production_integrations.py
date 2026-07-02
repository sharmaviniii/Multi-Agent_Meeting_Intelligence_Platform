from pathlib import Path

from meeting_intel.core.config import Settings
from meeting_intel.rag.embeddings import (
    HashEmbeddingModel,
    MockEmbeddingModel,
    get_embedding_model,
)
from meeting_intel.services.llm import LLMClient


def test_production_embedding_dependencies_are_self_contained():
    dependencies = Path("pyproject.toml").read_text(encoding="utf-8")

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
    settings = Settings(offline_mode=True, embedding_model="hash-embedding-384")

    model = get_embedding_model(settings)

    assert isinstance(model, MockEmbeddingModel)
    assert model.model_name == "hash-embedding-384"


def test_embedding_factory_uses_hash_model_in_production_mode_without_openai_key():
    settings = Settings(
        offline_mode=False,
        openai_api_key=None,
        embedding_model="hash-embedding-384",
    )

    model = get_embedding_model(settings)

    assert isinstance(model, HashEmbeddingModel)
    assert model.model_name == "hash-embedding-384"


def test_hash_embeddings_are_deterministic_and_dimensioned():
    model = HashEmbeddingModel(dimensions=384)

    first = model.embed_query("Asha will finish the API")
    second = model.embed_query("Asha will finish the API")

    assert first == second
    assert len(first) == 384
    assert any(value for value in first)
