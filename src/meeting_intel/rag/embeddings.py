import hashlib
import math
from functools import lru_cache

from meeting_intel.core.config import Settings


class MockEmbeddingModel:
    """Deterministic local embeddings for OFFLINE_MODE and tests."""

    def __init__(self, dimensions: int = 256) -> None:
        self.model_name = "mock-embedding"
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = digest[0] % self.dimensions
            vector[index] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class OpenAIEmbeddingModel:
    """OpenAI embeddings for production vector search."""

    def __init__(self, settings: Settings) -> None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required when OFFLINE_MODE=false")
        from openai import OpenAI

        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model_name = settings.embedding_model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = self.client.embeddings.create(model=self.model_name, input=texts)
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


@lru_cache
def get_embedding_model(settings: Settings) -> OpenAIEmbeddingModel | MockEmbeddingModel:
    if settings.offline_mode:
        return MockEmbeddingModel()
    return OpenAIEmbeddingModel(settings)
