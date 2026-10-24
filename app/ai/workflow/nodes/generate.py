from app.ai.llm import get_llm
from app.ai.prompts import load_prompt
from app.ai.workflow.state import AgentState


SAFE_REVIEW_MESSAGE = (
    "Thank you for contacting us. A support agent needs to review "
    "your message before we can provide an accurate answer."
)


def generate_response(state: AgentState) -> AgentState:
    """Generate a concise, knowledge-grounded email draft."""
    if state.get("error"):
        state["draft_response"] = SAFE_REVIEW_MESSAGE
        state["review_required"] = True
        return state

    email_text = (
        f"Subject: {state.get('subject', '')}\n"
        f"Body: {state.get('body', '')}"
    )

    context = "\n\n".join(state.get("retrieved_context", []))

    try:
        prompt = load_prompt("response_generation.txt").format(
            email=email_text,
            context=context or "No relevant knowledge was found.",
        )

        response = get_llm().invoke(prompt)
        draft = str(response.content).strip()

        if not draft:
            raise ValueError("The model returned an empty response.")

        state["draft_response"] = draft

        if not context:
            state["review_required"] = True

        state["status"] = "draft_generated"

    except Exception as exc:
        state["draft_response"] = SAFE_REVIEW_MESSAGE
        state["review_required"] = True
        state["status"] = "generation_failed"
        state["error"] = f"Response generation failed: {exc}"

    return state