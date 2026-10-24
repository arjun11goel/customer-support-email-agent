from app.ai.workflow.state import AgentState
from app.core.config import settings
from app.schemas.common import IntentCategory


AUTO_SEND_ALLOWED_INTENTS = {
    IntentCategory.PRODUCT_QUESTION.value,
}


def evaluate_escalation(state: AgentState) -> AgentState:
    """Decide whether to escalate, review, or simulate an automatic send."""
    escalation_reasons = []
    confidence = float(state.get("confidence", 0.0) or 0.0)
    retrieval_score = float(state.get("retrieval_score", 0.0) or 0.0)
    intent = state.get("intent", IntentCategory.OTHER.value)
    has_context = bool(state.get("retrieved_context"))
    validation_passed = state.get("validation_passed", False)

    if state.get("error"):
        escalation_reasons.append("An agent workflow step failed.")

    if confidence < settings.AGENT_CONFIDENCE_THRESHOLD:
        escalation_reasons.append(
            "Classification confidence is below the configured threshold."
        )

    if intent == IntentCategory.COMPLEX_ISSUE.value:
        escalation_reasons.append(
            "The email was classified as a complex issue."
        )

    if not has_context:
        escalation_reasons.append(
            "No relevant knowledge was retrieved."
        )

    if not validation_passed:
        escalation_reasons.append(
            "The draft did not pass the validation checks."
        )

    auto_send_eligible = (
        settings.AUTO_SEND_ENABLED
        and not escalation_reasons
        and intent in AUTO_SEND_ALLOWED_INTENTS
        and confidence >= settings.AUTO_SEND_CONFIDENCE_THRESHOLD
        and retrieval_score >= settings.AUTO_SEND_MIN_RETRIEVAL_SCORE
        and has_context
        and validation_passed
        and not state.get("error")
    )

    state["escalation_reasons"] = escalation_reasons
    state["escalation_required"] = bool(escalation_reasons)
    state["auto_send_eligible"] = auto_send_eligible
    state["review_required"] = not auto_send_eligible

    if auto_send_eligible:
        state["status"] = "auto_sent_demo"
        state["auto_send_reason"] = (
            "Allowed product question passed the confidence, retrieval, "
            "and validation checks."
        )
    elif escalation_reasons:
        state["status"] = "escalated"
        state["auto_send_reason"] = (
            "A safety check requires human review."
        )
    else:
        state["status"] = "awaiting_review"
        state["auto_send_reason"] = (
            "This case does not meet every demo auto-send requirement."
        )

    return state