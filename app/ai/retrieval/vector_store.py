from pathlib import Path


class VectorStoreManager:
    """
    Manages the FAISS vector store.

    Actual indexing and persistence will be implemented
    in the knowledge-base phase.
    """

    def __init__(self, path: str):
        self.path = Path(path)
        self.path.mkdir(
            parents=True,
            exist_ok=True,
        )

    def exists(self) -> bool:
        """Return whether the vector store directory exists."""

        return self.path.exists()