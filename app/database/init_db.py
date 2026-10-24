from sqlalchemy import inspect, text

from app.database.connection import Base, engine

# Import models so SQLAlchemy knows about their tables.
from app.models import (  # noqa: F401
    agent_run,
    email,
    response,
    user,
)


SQLITE_AGENT_RUN_COLUMNS = {
    "grounding_score": "FLOAT",
    "validation_passed": "BOOLEAN",
    "validation_issues": "TEXT",
    "review_required": "BOOLEAN NOT NULL DEFAULT 1",
    "escalation_reasons": "TEXT",
    "error": "TEXT",
}


def initialize_database() -> None:
    """Create tables and add new AgentRun columns to an existing SQLite DB."""
    Base.metadata.create_all(bind=engine)

    if engine.dialect.name != "sqlite":
        return

    existing_columns = {
        column["name"]
        for column in inspect(engine).get_columns("agent_runs")
    }

    with engine.begin() as connection:
        for column_name, column_type in SQLITE_AGENT_RUN_COLUMNS.items():
            if column_name not in existing_columns:
                connection.execute(
                    text(
                        f"ALTER TABLE agent_runs "
                        f"ADD COLUMN {column_name} {column_type}"
                    )
                )