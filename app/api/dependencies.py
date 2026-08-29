from collections.abc import Generator

from sqlalchemy.orm import Session

from app.database.connection import get_db


def get_database() -> Generator[Session, None, None]:
    """Provide a database session to API routes."""

    yield from get_db()