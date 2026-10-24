import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer


class LocalTextEmbeddings:
    """Create small local vectors from words and two-word phrases."""

    def __init__(self) -> None:
        self.vectorizer = HashingVectorizer(
            n_features=512,
            alternate_sign=False,
            norm="l2",
            ngram_range=(1, 2),
            lowercase=True,
            dtype=np.float32,
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Convert document text into normalized vectors."""
        if not texts:
            return []

        vectors = self.vectorizer.transform(texts)
        return vectors.toarray().astype(np.float32).tolist()

    def embed_query(self, text: str) -> list[float]:
        """Convert a customer email or search query into one vector."""
        vectors = self.vectorizer.transform([text])
        return vectors.toarray()[0].astype(np.float32).tolist()


def get_embeddings(model_name: str | None = None) -> LocalTextEmbeddings:
    """Return the local vectorizer; model_name is kept for compatibility."""
    _ = model_name
    return LocalTextEmbeddings()