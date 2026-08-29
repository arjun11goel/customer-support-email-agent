from langchain_community.embeddings import HuggingFaceEmbeddings


def get_embeddings(model_name: str):
    """Create the local embedding model."""

    return HuggingFaceEmbeddings(
        model_name=model_name,
    )