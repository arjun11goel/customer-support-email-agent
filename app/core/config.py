from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    APP_NAME: str = "SupportFlow AI"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000

    DATABASE_URL: str = "sqlite:///./data/app.db"

    LLM_PROVIDER: str = "local"
    LLM_MODEL: str = "local-model"
    LLM_BASE_URL: str | None = None
    LLM_API_KEY: str | None = None

    EMBEDDING_MODEL: str = (
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    VECTOR_STORE_PATH: str = "data/vector_store"

    AGENT_CONFIDENCE_THRESHOLD: float = 0.85

    AUTO_SEND_ENABLED: bool = False

    BACKEND_URL: str = "http://127.0.0.1:8000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()