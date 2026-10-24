from langchain_openai import ChatOpenAI

from app.core.config import settings


GEMINI_OPENAI_BASE_URL = (
    "https://generativelanguage.googleapis.com/v1beta/openai/"
)


def get_llm() -> ChatOpenAI:
    """Create the Gemini chat model using the OpenAI-compatible interface."""
    provider = settings.LLM_PROVIDER.strip().lower()

    if provider != "gemini":
        raise RuntimeError(
            "LLM_PROVIDER must be set to 'gemini' for this project."
        )

    if not settings.LLM_API_KEY:
        raise RuntimeError(
            "LLM_API_KEY is empty. Add your Gemini API key to the local .env."
        )

    configured_base_url = (
        settings.LLM_BASE_URL or GEMINI_OPENAI_BASE_URL
    ).rstrip("/")

    expected_base_url = GEMINI_OPENAI_BASE_URL.rstrip("/")

    if configured_base_url != expected_base_url:
        raise RuntimeError(
            "LLM_BASE_URL must use the Gemini OpenAI-compatible endpoint."
        )

    if not settings.LLM_MODEL:
        raise RuntimeError("LLM_MODEL must contain a Gemini model name.")

    return ChatOpenAI(
        model=settings.LLM_MODEL,
        api_key=settings.LLM_API_KEY,
        base_url=GEMINI_OPENAI_BASE_URL,
        temperature=0,
        timeout=30,
        max_retries=2,
    )