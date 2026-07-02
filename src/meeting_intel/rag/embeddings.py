import hashlib
import math
from functools import lru_cache

from meeting_intel.core.config import Settings


class HashEmbeddingModel:
    """Deterministic, dependency-free embeddings for Chroma retrieval."""

    def __init__(self, model_name: str = "hash-embedding-384", dimensions: int = 384) -> None:
        self.model_name = model_name
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            weight = 1.0 + (digest[4] / 255.0)
            vector[index] += weight
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


MockEmbeddingModel = HashEmbeddingModel


@lru_cache
def get_embedding_model(settings: Settings) -> HashEmbeddingModel:
    return HashEmbeddingModel(model_name=settings.embedding_model)