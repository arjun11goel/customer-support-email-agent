from app.ai.workflow.state import AgentState


def evaluate_escalation(state: AgentState) -> AgentState:
    """
    Placeholder escalation node.

    Complex-issue routing and confidence thresholds
    will be implemented later.
    """

    state["escalation_required"] = False

    return state