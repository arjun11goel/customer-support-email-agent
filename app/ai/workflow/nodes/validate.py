import re

from app.ai.workflow.state import AgentState


STOP_WORDS = {
    "about", "after", "also", "are", "been", "being", "but", "can",
    "could", "dear", "does", "for", "from", "hello", "here", "into",
    "its", "just", "more", "most", "our", "please", "regards", "should",
    "that", "their", "them", "then", "there", "these", "they", "this",
    "those", "through", "thank", "thanks", "very", "was", "were", "with",
    "would", "your",
}

NUMBER_PATTERN = re.compile(r"\b\d+(?:\.\d+)?\b|[$₹]\s?\d+(?:\.\d+)?")


def _content_words(text: str) -> set[str]:
    """Return meaningful lowercase words from text."""
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    return {word for word in words if word not in STOP_WORDS}


def validate_response(state: AgentState) -> AgentState:
    """Check draft presence and estimate its overlap with retrieved knowledge."""
    draft = state.get("draft_response", "").strip()
    context = "\n".join(state.get("retrieved_context", []))
    issues = []

    if not draft:
        issues.append("The response draft is empty.")

    context_words = _content_words(context)
    draft_words = _content_words(draft)

    if not context_words:
        grounding_score = 0.0
        issues.append("No relevant knowledge was retrieved.")
    elif not draft_words:
        grounding_score = 0.0
    else:
        overlap = draft_words.intersection(context_words)
        grounding_score = len(overlap) / len(draft_words)

        if grounding_score < 0.20:
            issues.append(
                "The draft has little wording overlap with the retrieved "
                "knowledge."
            )

    draft_numbers = set(NUMBER_PATTERN.findall(draft))
    context_numbers = set(NUMBER_PATTERN.findall(context))

    if draft_numbers - context_numbers:
        issues.append(
            "The draft contains a number or amount absent from the "
            "retrieved knowledge."
        )

    state["grounding_score"] = round(grounding_score, 3)
    state["validation_issues"] = issues
    state["validation_passed"] = not issues

    # A person must approve every draft before it can be sent.
    state["review_required"] = True
    state["status"] = "awaiting_review"

    return state