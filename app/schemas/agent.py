from pydantic import BaseModel, Field

from app.schemas.common import IntentCategory


class AgentRunResponse(BaseModel):
    """Agent workflow result returned by the API."""

    run_id: str
    email_id: str
    response_id: str | None = None

    intent: IntentCategory | None = None
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    retrieved_context: list[str] = Field(default_factory=list)
    draft_response: str | None = None

    grounding_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )
    validation_passed: bool | None = None
    validation_issues: list[str] = Field(default_factory=list)

    review_required: bool = True
    escalation_required: bool = False
    escalation_reasons: list[str] = Field(default_factory=list)

    error: str | None = None
    status: str


class AgentStateResponse(BaseModel):
    """Agent state fields used by the UI."""

    email_id: str
    intent: IntentCategory | None = None
    confidence: float | None = None

    retrieved_context: list[str] = Field(default_factory=list)
    draft_response: str | None = None

    grounding_score: float | None = None
    validation_passed: bool | None = None
    validation_issues: list[str] = Field(default_factory=list)

    escalation_required: bool = False
    escalation_reasons: list[str] = Field(default_factory=list)
    review_required: bool = True

    error: str | None = None
    status: str = "started"