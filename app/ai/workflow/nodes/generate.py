from app.ai.workflow.state import AgentState


def generate_response(state: AgentState) -> AgentState:
    """
    Placeholder response generation node.

    LLM-based generation will be implemented later.
    """

    state["draft_response"] = (
        "Agent response generation is not implemented yet."
    )

    return state