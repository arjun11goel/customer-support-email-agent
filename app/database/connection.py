from pathlib import Path
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


database_url = make_url(settings.DATABASE_URL)
connect_args = {}

if database_url.get_backend_name() == "sqlite":
    connect_args = {"check_same_thread": False}
    database_name = database_url.database

    if database_name and database_name != ":memory:":
        Path(database_name).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and close it after the request."""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()