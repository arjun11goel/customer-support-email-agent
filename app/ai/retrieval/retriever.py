class KnowledgeRetriever:
    """
    Retrieval abstraction.

    The concrete FAISS implementation will be connected
    after the initial scaffold is verified.
    """

    def retrieve(
        self,
        query: str,
        top_k: int = 4,
    ) -> list[str]:
        """Retrieve relevant knowledge documents."""

        return []