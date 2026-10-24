from typing import TypedDict


class AgentState(TypedDict, total=False):
    """Shared data passed from one LangGraph node to the next."""

    email_id: str
    sender: str
    recipient: str
    subject: str
    body: str

    intent: str
    confidence: float

    retrieved_context: list[str]
    retrieval_score: float
    draft_response: str

    grounding_score: float
    validation_issues: list[str]
    validation_passed: bool

    escalation_required: bool
    escalation_reasons: list[str]
    review_required: bool

    auto_send_eligible: bool
    auto_send_reason: str

    status: str
    error: str | None