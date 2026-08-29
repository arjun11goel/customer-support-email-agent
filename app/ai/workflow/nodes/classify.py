from app.ai.workflow.state import AgentState


def classify_email(state: AgentState) -> AgentState:
    """
    Placeholder classification node.

    The actual LLM-based structured classification
    will be implemented in the next phase.
    """

    state["status"] = "classified"

    # Temporary placeholder.
    state["intent"] = "other"
    state["confidence"] = 0.0

    return state