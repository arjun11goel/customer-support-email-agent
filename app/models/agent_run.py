from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class AgentRun(Base):
    """Store the result of one agent workflow execution."""

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

    grounding_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    validation_passed: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    validation_issues: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    review_required: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    escalation_required: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    escalation_reasons: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
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