from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

from app.ai.llm import get_llm
from app.ai.prompts import load_prompt
from app.ai.workflow.state import AgentState
from app.schemas.common import IntentCategory


class ClassificationResult(BaseModel):
    """The fields the classifier must return."""

    intent: IntentCategory
    confidence: float = Field(ge=0.0, le=1.0)


def classify_email(state: AgentState) -> AgentState:
    """Classify the customer email and record the model's confidence."""
    email_text = (
        f"Subject: {state.get('subject', '')}\n"
        f"Body: {state.get('body', '')}"
    )

    prompt = load_prompt("classification.txt").format(email=email_text)
    prompt += (
        "\n\nReturn only a JSON object with these fields:\n"
        '{"intent": "one allowed category", "confidence": 0.0}\n'
        "The confidence must be a number from 0.0 to 1.0."
    )

    try:
        response = get_llm().invoke(prompt)
        parsed = JsonOutputParser().parse(str(response.content))
        result = ClassificationResult.model_validate(parsed)

        state["intent"] = result.intent.value
        state["confidence"] = result.confidence
        state["status"] = "classified"

    except Exception as exc:
        # Do not present a failed model call as a successful classification.
        state["intent"] = IntentCategory.OTHER.value
        state["confidence"] = 0.0
        state["review_required"] = True
        state["status"] = "classification_failed"
        state["error"] = f"Classification failed: {exc}"

    return state