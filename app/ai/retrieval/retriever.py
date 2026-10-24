from app.ai.retrieval.vector_store import VectorStoreManager
from app.core.config import settings


class KnowledgeRetriever:
    """Find relevant knowledge-base chunks for a customer email."""

    MIN_RELEVANCE_SCORE = 0.05

    def __init__(self, vector_store_path: str | None = None):
        path = vector_store_path or settings.VECTOR_STORE_PATH
        self.vector_store = VectorStoreManager(path)

    def retrieve_with_score(
        self,
        query: str,
        top_k: int = 4,
    ) -> tuple[list[str], float]:
        """Return relevant excerpts and their highest similarity score."""
        if not query.strip():
            return [], 0.0

        matches = self.vector_store.search(query, top_k=top_k)
        results = []
        best_score = 0.0

        for match in matches:
            score = float(match["score"])

            if score < self.MIN_RELEVANCE_SCORE:
                continue

            results.append(
                f"Source: {match['source']}\n"
                f"Excerpt: {match['text']}"
            )
            best_score = max(best_score, score)

        return results, best_score

    def retrieve(
        self,
        query: str,
        top_k: int = 4,
    ) -> list[str]:
        """Return relevant excerpts with their source filenames."""
        results, _ = self.retrieve_with_score(query, top_k=top_k)
        return results