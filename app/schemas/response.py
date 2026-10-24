from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ResponseResponse(BaseModel):
    """Saved response details returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    email_id: str
    agent_run_id: str
    content: str
    status: str
    approved_by: str | None = None
    sent_at: datetime | None = None


class ApproveResponseRequest(BaseModel):
    """Who approved a draft."""

    approved_by: str = Field(
        default="support_agent",
        min_length=1,
        max_length=255,
    )


class UpdateResponseRequest(BaseModel):
    """Edited content for a response draft."""

    content: str = Field(
        min_length=1,
        max_length=20000,
    )