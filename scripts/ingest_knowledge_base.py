from app.services.knowledge_base_service import KnowledgeBaseService


def main() -> None:
    """Build the FAISS index from the Markdown knowledge files."""
    service = KnowledgeBaseService()
    result = service.rebuild_index()

    print(
        f"Indexed {result['chunks_indexed']} chunks "
        f"from {result['documents_indexed']} knowledge-base files."
    )
    print(f"FAISS index saved to: {service.vector_store_path}")


if __name__ == "__main__":
    main()