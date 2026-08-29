from app.ai.workflow.state import AgentState


def retrieve_knowledge(state: AgentState) -> AgentState:
    """
    Placeholder retrieval node.

    FAISS retrieval will be connected here later.
    """

    state["retrieved_context"] = []

    return state