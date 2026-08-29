from pathlib import Path


class KnowledgeBaseService:
    """Knowledge-base management service."""

    def __init__(
        self,
        knowledge_base_path: str = "data/knowledge_base",
    ):
        self.path = Path(knowledge_base_path)

    def list_documents(self) -> list[str]:
        """Return available knowledge-base documents."""

        if not self.path.exists():
            return []

        return sorted(
            file.name
            for file in self.path.glob("*.md")
        )

    def read_document(self, filename: str) -> str:
        """Read a knowledge-base document."""

        file_path = self.path / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Knowledge document '{filename}' not found."
            )

        return file_path.read_text(
            encoding="utf-8"
        )