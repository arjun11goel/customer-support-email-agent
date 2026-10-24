import argparse
import json
import time
from pathlib import Path
from typing import Any

from app.ai.workflow.graph import agent_graph
from app.core.config import settings
from app.services.knowledge_base_service import KnowledgeBaseService


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_DATA_PATH = (
    PROJECT_ROOT / "tests" / "fixtures" / "evaluation_emails.json"
)
RESULTS_PATH = PROJECT_ROOT / "data" / "evaluation_results.json"


def percentage(numerator: int, denominator: int) -> float | None:
    """Return a percentage, or None when there is nothing to measure."""
    if denominator == 0:
        return None

    return round((numerator / denominator) * 100, 2)


def evaluate_email(email: dict[str, Any]) -> dict[str, Any]:
    """Run one labeled email through the complete agent workflow."""
    initial_state = {
        "email_id": email["id"],
        "sender": email["sender"],
        "recipient": email["recipient"],
        "subject": email["subject"],
        "body": email["body"],
    }

    started_at = time.perf_counter()
    result = agent_graph.invoke(initial_state)
    latency_seconds = round(time.perf_counter() - started_at, 2)

    expected_source = email.get("expected_source")
    retrieved_context = result.get("retrieved_context", [])

    source_found = None
    if expected_source:
        source_found = any(
            f"Source: {expected_source}" in context_item
            for context_item in retrieved_context
        )

    error = result.get("error")
    classification_succeeded = not (
        isinstance(error, str) and error.startswith("Classification failed:")
    )

    predicted_intent = result.get("intent")
    expected_intent = email["expected_intent"]

    return {
        "id": email["id"],
        "expected_intent": expected_intent,
        "predicted_intent": predicted_intent,
        "classification_correct": (
            predicted_intent == expected_intent
            if classification_succeeded
            else None
        ),
        "classification_succeeded": classification_succeeded,
        "expected_source": expected_source,
        "retrieval_source_found": source_found,
        "validation_passed": result.get("validation_passed"),
        "escalation_required": result.get("escalation_required", False),
        "auto_send_eligible": result.get("auto_send_eligible", False),
        "auto_send_reason": result.get("auto_send_reason"),
        "latency_seconds": latency_seconds,
        "error": error,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate SupportFlow AI using labeled email examples."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Evaluate only the first N examples. Omit for the full dataset.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=5.0,
        help="Seconds to wait between emails to reduce API rate-limit errors.",
    )
    args = parser.parse_args()

    if not EVALUATION_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Evaluation dataset not found: {EVALUATION_DATA_PATH}"
        )

    emails = json.loads(EVALUATION_DATA_PATH.read_text(encoding="utf-8"))

    if args.limit is not None:
        emails = emails[: args.limit]

    if not emails:
        raise ValueError("The evaluation dataset contains no examples.")

    print("Rebuilding the local knowledge index...")
    index_result = KnowledgeBaseService().rebuild_index()
    print(
        f"Indexed {index_result['chunks_indexed']} chunks "
        f"from {index_result['documents_indexed']} files."
    )
    print(f"Evaluating {len(emails)} emails...")
    print(f"Simulated auto-send enabled: {settings.AUTO_SEND_ENABLED}")

    case_results = []

    for index, email in enumerate(emails):
        print(f"[{index + 1}/{len(emails)}] {email['id']}")

        try:
            case_result = evaluate_email(email)
        except Exception as exc:
            case_result = {
                "id": email["id"],
                "expected_intent": email["expected_intent"],
                "predicted_intent": None,
                "classification_correct": None,
                "classification_succeeded": False,
                "expected_source": email.get("expected_source"),
                "retrieval_source_found": None,
                "validation_passed": None,
                "escalation_required": None,
                "auto_send_eligible": False,
                "auto_send_reason": (
                    "Evaluation failed before the policy decision."
                ),
                "latency_seconds": None,
                "error": str(exc),
            }

        case_results.append(case_result)

        if index < len(emails) - 1 and args.delay > 0:
            time.sleep(args.delay)

    successful_classifications = [
        result
        for result in case_results
        if result["classification_succeeded"]
    ]
    correct_classifications = sum(
        result["classification_correct"] is True
        for result in successful_classifications
    )

    retrieval_cases = [
        result
        for result in case_results
        if result["expected_source"] is not None
    ]
    successful_retrievals = sum(
        result["retrieval_source_found"] is True
        for result in retrieval_cases
    )

    validation_cases = [
        result
        for result in case_results
        if result["validation_passed"] is not None
    ]
    passed_validations = sum(
        result["validation_passed"] is True
        for result in validation_cases
    )

    completed_runs = [
        result
        for result in case_results
        if result["escalation_required"] is not None
    ]
    escalated_runs = sum(
        result["escalation_required"] is True
        for result in completed_runs
    )

    auto_send_eligible_cases = sum(
        result["auto_send_eligible"] is True
        for result in case_results
    )

    latencies = [
        result["latency_seconds"]
        for result in case_results
        if result["latency_seconds"] is not None
    ]

    summary = {
        "examples_total": len(case_results),
        "classification_coverage_percent": percentage(
            len(successful_classifications),
            len(case_results),
        ),
        "classification_accuracy_percent": percentage(
            correct_classifications,
            len(successful_classifications),
        ),
        "retrieval_source_hit_rate_percent": percentage(
            successful_retrievals,
            len(retrieval_cases),
        ),
        "retrieval_cases_with_expected_source": len(retrieval_cases),
        "validation_pass_rate_percent": percentage(
            passed_validations,
            len(validation_cases),
        ),
        "escalation_rate_percent": percentage(
            escalated_runs,
            len(completed_runs),
        ),
        "auto_send_enabled": settings.AUTO_SEND_ENABLED,
        "auto_send_eligible_cases": auto_send_eligible_cases,
        "auto_send_eligibility_rate_percent": percentage(
            auto_send_eligible_cases,
            len(case_results),
        ),
        "average_latency_seconds": (
            round(sum(latencies) / len(latencies), 2)
            if latencies
            else None
        ),
        "classification_failures": (
            len(case_results) - len(successful_classifications)
        ),
    }

    report = {
        "summary": summary,
        "cases": case_results,
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\nEvaluation summary")
    print(json.dumps(summary, indent=2))
    print(f"\nDetailed results saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    main()