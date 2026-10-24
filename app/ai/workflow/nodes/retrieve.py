from app.ai.retrieval.retriever import KnowledgeRetriever
from app.ai.workflow.state import AgentState


def retrieve_knowledge(state: AgentState) -> AgentState:
    """Find relevant knowledge excerpts and keep the best match score."""
    if state.get("error"):
        state["retrieved_context"] = []
        state["retrieval_score"] = 0.0
        state["review_required"] = True
        return state

    query = (
        f"{state.get('subject', '')}\n"
        f"{state.get('body', '')}"
    ).strip()

    try:
        context, best_score = KnowledgeRetriever().retrieve_with_score(
            query,
            top_k=4,
        )

        state["retrieved_context"] = context
        state["retrieval_score"] = best_score

        if not context:
            state["review_required"] = True

    except Exception as exc:
        state["retrieved_context"] = []
        state["retrieval_score"] = 0.0
        state["review_required"] = True
        state["status"] = "retrieval_failed"
        state["error"] = f"Knowledge retrieval failed: {exc}"

    return state