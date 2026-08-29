from app.ai.workflow.state import AgentState


def validate_response(state: AgentState) -> AgentState:
    """
    Placeholder response validation node.

    Guardrails and groundedness checks will be implemented later.
    """

    state["review_required"] = True
    state["status"] = "awaiting_review"

    return state