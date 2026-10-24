from pathlib import Path

from app.ai.retrieval.vector_store import VectorStoreManager
from app.core.config import settings


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class KnowledgeBaseService:
    """Read knowledge documents and build the FAISS search index."""

    def __init__(self, knowledge_base_path: str | None = None):
        configured_path = Path(
            knowledge_base_path or "data/knowledge_base"
        )

        if not configured_path.is_absolute():
            configured_path = PROJECT_ROOT / configured_path

        self.path = configured_path.resolve()

        vector_store_path = Path(settings.VECTOR_STORE_PATH)

        if not vector_store_path.is_absolute():
            vector_store_path = PROJECT_ROOT / vector_store_path

        self.vector_store_path = vector_store_path.resolve()

    def list_documents(self) -> list[str]:
        """Return the names of available Markdown documents."""
        if not self.path.exists():
            return []

        return sorted(
            file_path.name
            for file_path in self.path.glob("*.md")
            if file_path.is_file()
        )

    def read_document(self, filename: str) -> str:
        """Read one Markdown document without leaving the knowledge folder."""
        file_path = (self.path / filename).resolve()

        try:
            file_path.relative_to(self.path)
        except ValueError as exc:
            raise FileNotFoundError("Invalid knowledge document path.") from exc

        if file_path.suffix.lower() != ".md" or not file_path.is_file():
            raise FileNotFoundError(
                f"Knowledge document '{filename}' was not found."
            )

        return file_path.read_text(encoding="utf-8")

    @staticmethod
    def _split_into_chunks(
        text: str,
        chunk_words: int = 150,
        overlap_words: int = 25,
    ) -> list[str]:
        """Split document text into overlapping word chunks."""
        words = text.split()

        if not words:
            return []

        step = chunk_words - overlap_words
        chunks = []

        for start in range(0, len(words), step):
            chunks.append(" ".join(words[start : start + chunk_words]))

            if start + chunk_words >= len(words):
                break

        return chunks

    def rebuild_index(self) -> dict[str, int]:
        """Read all Markdown files and replace the saved FAISS index."""
        files = sorted(self.path.glob("*.md"))

        if not files:
            raise ValueError(
                f"No Markdown knowledge files found in '{self.path}'."
            )

        indexed_chunks = []

        for file_path in files:
            content = file_path.read_text(encoding="utf-8")

            for chunk in self._split_into_chunks(content):
                indexed_chunks.append(
                    {
                        "source": file_path.name,
                        "text": chunk,
                    }
                )

        vector_store = VectorStoreManager(str(self.vector_store_path))
        vector_store.build(indexed_chunks)

        return {
            "documents_indexed": len(files),
            "chunks_indexed": len(indexed_chunks),
        }