from app.database.connection import Base, engine

# Import models so SQLAlchemy knows about them.
from app.models import agent_run, email, follow_up, response  # noqa: F401


def initialize_database() -> None:
    """Create database tables if they do not already exist."""

    Base.metadata.create_all(bind=engine)