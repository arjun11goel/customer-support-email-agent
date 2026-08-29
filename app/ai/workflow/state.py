from typing import TypedDict


class AgentState(TypedDict, total=False):
    """Shared state passed between LangGraph nodes."""

    email_id: str
    sender: str
    recipient: str
    subject: str
    body: str

    intent: str
    confidence: float

    retrieved_context: list[str]

    draft_response: str

    escalation_required: bool
    review_required: bool

    status: str

    error: str | None