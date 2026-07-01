import hashlib
import math
from functools import lru_cache


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


class LocalEmbeddingModel:
    """SentenceTransformer wrapper for BAAI/bge-small-en-v1.5."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5") -> None:
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


@lru_cache
def get_embedding_model(
    model_name: str = "BAAI/bge-small-en-v1.5", offline_mode: bool = False
) -> LocalEmbeddingModel | MockEmbeddingModel:
    if offline_mode:
        return MockEmbeddingModel()
    return LocalEmbeddingModel(model_name)
