from langchain_openai import ChatOpenAI

from app.core.config import settings


def get_llm():
    """
    Create the configured chat model.

    The provider is intentionally abstracted so that
    we can later use a local or free OpenAI-compatible
    provider without changing the agent workflow.
    """

    if not settings.LLM_API_KEY:
        raise RuntimeError(
            "LLM_API_KEY is not configured. "
            "The LLM integration will be enabled in a later phase."
        )

    kwargs = {
        "model": settings.LLM_MODEL,
        "api_key": settings.LLM_API_KEY,
        "temperature": 0,
    }

    if settings.LLM_BASE_URL:
        kwargs["base_url"] = settings.LLM_BASE_URL

    return ChatOpenAI(**kwargs)