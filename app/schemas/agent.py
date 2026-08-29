from pydantic import BaseModel, Field

from app.schemas.common import IntentCategory


class AgentRunResponse(BaseModel):
    """Agent execution response."""

    run_id: str
    email_id: str

    intent: IntentCategory | None = None

    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    retrieved_context: list[str] = []

    draft_response: str | None = None

    escalation_required: bool = False

    status: str


class AgentStateResponse(BaseModel):
    """Simplified agent state for UI/API consumption."""

    email_id: str
    intent: IntentCategory | None = None
    confidence: float | None = None
    retrieved_context: list[str] = []
    draft_response: str | None = None
    escalation_required: bool = False
    review_required: bool = True
    status: str = "started"