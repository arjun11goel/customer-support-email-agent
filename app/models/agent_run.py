from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class AgentRun(Base):
    """Stores an execution of the AI agent."""

    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    email_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("emails.id"),
        nullable=False,
    )

    intent: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    retrieved_context: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    draft_response: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    escalation_required: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="started",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )