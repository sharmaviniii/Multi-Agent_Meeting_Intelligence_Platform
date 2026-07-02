from pathlib import Path

from meeting_intel.core.config import Settings
from meeting_intel.rag.chunking import TextChunk
from meeting_intel.rag.embeddings import HashEmbeddingModel


def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=False))


class InMemoryMeetingStore:
    def __init__(self, embedding_model: HashEmbeddingModel) -> None:
        self.embedding_model = embedding_model
        self._records: dict[str, dict] = {}

    def upsert_chunks(self, chunks: list[TextChunk]) -> None:
        embeddings = self.embedding_model.embed_documents([chunk.text for chunk in chunks])
        for chunk, embedding in zip(chunks, embeddings, strict=True):
            self._records[chunk.id] = {
                "text": chunk.text,
                "metadata": chunk.metadata,
                "embedding": embedding,
            }

    def search(
        self,
        query: str,
        top_k: int = 5,
        meeting_id: str | None = None,
        artifact_type: str | None = None,
    ) -> list[dict]:
        query_embedding = self.embedding_model.embed_query(query)
        hits = []
        for record_id, record in self._records.items():
            metadata = record["metadata"]
            if meeting_id and metadata.get("meeting_id") != meeting_id:
                continue
            if artifact_type and metadata.get("artifact_type") != artifact_type:
                continue
            hits.append(
                {
                    "id": record_id,
                    "text": record["text"],
                    "metadata": metadata,
                    "score": cosine_similarity(query_embedding, record["embedding"]),
                }
            )
        return sorted(hits, key=lambda hit: hit["score"], reverse=True)[:top_k]


class ChromaMeetingStore:
    def __init__(
        self,
        settings: Settings,
        embedding_model: HashEmbeddingModel,
    ) -> None:
        self.settings = settings
        self.embedding_model = embedding_model
        self._collection = None
        self._memory = InMemoryMeetingStore(embedding_model)

    @property
    def collection(self):
        if self.settings.offline_mode:
            return None
        if self._collection is None:
            import chromadb

            chroma_path = Path(self.settings.chroma_path)
            chroma_path.mkdir(parents=True, exist_ok=True)
            client = chromadb.PersistentClient(path=str(chroma_path))
            self._collection = client.get_or_create_collection(
                self.settings.chroma_collection,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def upsert_chunks(self, chunks: list[TextChunk]) -> None:
        if not chunks:
            return
        if self.settings.offline_mode:
            self._memory.upsert_chunks(chunks)
            return
        embeddings = self.embedding_model.embed_documents([chunk.text for chunk in chunks])
        self.collection.upsert(
            ids=[chunk.id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            metadatas=[chunk.metadata for chunk in chunks],
            embeddings=embeddings,
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
        meeting_id: str | None = None,
        artifact_type: str | None = None,
    ) -> list[dict]:
        if self.settings.offline_mode:
            return self._memory.search(query, top_k, meeting_id, artifact_type)

        where = {}
        if meeting_id:
            where["meeting_id"] = meeting_id
        if artifact_type:
            where["artifact_type"] = artifact_type
        where_filter = where or None
        result = self.collection.query(
            query_embeddings=[self.embedding_model.embed_query(query)],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        return [
            {"text": doc, "metadata": meta, "score": 1.0 - float(distance)}
            for doc, meta, distance in zip(documents, metadatas, distances, strict=False)
        ]


def rerank(query: str, hits: list[dict]) -> list[dict]:
    terms = {term.lower() for term in query.split() if len(term) > 3}
    return sorted(
        hits,
        key=lambda hit: (
            0.2 * sum(1 for term in terms if term in hit["text"].lower()),
            hit.get("score", 0),
        ),
        reverse=True,
    )
