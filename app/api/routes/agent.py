import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_database
from app.core.exceptions import AppException
from app.models.agent_run import AgentRun
from app.schemas.agent import AgentRunResponse
from app.services.agent_service import AgentService
from app.services.response_service import ResponseService

router = APIRouter()


def _json_list(value: str | None) -> list[str]:
    """Read a saved JSON list, returning an empty list if invalid."""
    if not value:
        return []

    try:
        result = json.loads(value)
    except json.JSONDecodeError:
        return []

    if not isinstance(result, list):
        return []

    return [str(item) for item in result]


def _make_response(
    run: AgentRun,
    db: Session,
) -> AgentRunResponse:
    """Convert a saved agent run into the public API response."""
    response = ResponseService(db).get_for_agent_run(run.id)

    context = [
        item.strip()
        for item in (run.retrieved_context or "").split("\n\n")
        if item.strip()
    ]

    return AgentRunResponse(
        run_id=run.id,
        email_id=run.email_id,
        response_id=response.id if response else None,
        intent=run.intent,
        confidence=run.confidence,
        retrieved_context=context,
        draft_response=run.draft_response,
        grounding_score=run.grounding_score,
        validation_passed=run.validation_passed,
        validation_issues=_json_list(run.validation_issues),
        review_required=run.review_required,
        escalation_required=run.escalation_required,
        escalation_reasons=_json_list(run.escalation_reasons),
        error=run.error,
        status=run.status,
    )


@router.post(
    "/agent/run/{email_id}",
    response_model=AgentRunResponse,
)
def run_agent(
    email_id: str,
    db: Session = Depends(get_database),
):
    """Run the support workflow for one saved email."""
    try:
        run = AgentService(db).run(email_id)
        return _make_response(run, db)
    except AppException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
        ) from exc


@router.get(
    "/agent/runs/{email_id}",
    response_model=AgentRunResponse | None,
)
def get_latest_agent_run(
    email_id: str,
    db: Session = Depends(get_database),
):
    """Return the latest saved workflow run for one email."""
    run = AgentService(db).get_latest_run(email_id)

    if not run:
        return None

    return _make_response(run, db)