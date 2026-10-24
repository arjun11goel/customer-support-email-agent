import json
from pathlib import Path

import faiss
import numpy as np

from app.ai.retrieval.embeddings import get_embeddings


class VectorStoreManager:
    """Build, save, load, and search the FAISS knowledge index."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.index_path = self.path / "knowledge.faiss"
        self.documents_path = self.path / "documents.json"

        self.index = None
        self.documents: list[dict[str, str]] = []

    def exists(self) -> bool:
        """Return True when both saved index files are present."""
        return self.index_path.exists() and self.documents_path.exists()

    def build(self, documents: list[dict[str, str]]) -> None:
        """Create a new FAISS index from text chunks and source names."""
        cleaned_documents = []

        for document in documents:
            text = document.get("text", "").strip()

            if text:
                cleaned_documents.append(
                    {
                        "text": text,
                        "source": document.get("source", "unknown"),
                    }
                )

        if not cleaned_documents:
            raise ValueError("There are no non-empty documents to index.")

        embeddings = get_embeddings().embed_documents(
            [document["text"] for document in cleaned_documents]
        )
        vectors = np.asarray(embeddings, dtype=np.float32)

        # The embedding vectors are normalized, so inner product ranks them
        # by cosine similarity.
        self.index = faiss.IndexFlatIP(vectors.shape[1])
        self.index.add(vectors)
        self.documents = cleaned_documents

        self.save()

    def save(self) -> None:
        """Persist the FAISS index and its text chunks."""
        if self.index is None:
            raise ValueError("Build or load an index before saving it.")

        self.path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))

        self.documents_path.write_text(
            json.dumps(self.documents, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def load(self) -> None:
        """Load the saved FAISS index and matching text chunks."""
        if not self.exists():
            raise FileNotFoundError(
                f"No saved knowledge index found in '{self.path}'. "
                "Run the knowledge ingestion script first."
            )

        self.index = faiss.read_index(str(self.index_path))
        self.documents = json.loads(
            self.documents_path.read_text(encoding="utf-8")
        )

    def search(
        self,
        query: str,
        top_k: int = 4,
    ) -> list[dict[str, str | float]]:
        """Return the most relevant text chunks for a query."""
        if top_k <= 0 or not query.strip():
            return []

        if self.index is None:
            if not self.exists():
                return []
            self.load()

        if self.index is None or self.index.ntotal == 0:
            return []

        query_embedding = get_embeddings().embed_query(query)
        query_vector = np.asarray(
            [query_embedding],
            dtype=np.float32,
        )

        result_count = min(top_k, self.index.ntotal)
        scores, positions = self.index.search(query_vector, result_count)

        results: list[dict[str, str | float]] = []

        for score, position in zip(scores[0], positions[0]):
            if position < 0:
                continue

            document = self.documents[int(position)]

            results.append(
                {
                    "text": document["text"],
                    "source": document["source"],
                    "score": float(score),
                }
            )

        return results