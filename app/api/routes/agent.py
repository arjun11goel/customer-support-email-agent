from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_database
from app.schemas.agent import AgentRunResponse
from app.services.agent_service import AgentService

router = APIRouter()


@router.post(
    "/agent/run/{email_id}",
    response_model=AgentRunResponse,
)
def run_agent(
    email_id: str,
    db: Session = Depends(get_database),
):
    service = AgentService(db)

    run = service.run(email_id)

    context = []

    if run.retrieved_context:
        context = [
            item.strip()
            for item in run.retrieved_context.split("\n\n")
            if item.strip()
        ]

    return AgentRunResponse(
        run_id=run.id,
        email_id=run.email_id,
        intent=run.intent,
        confidence=run.confidence,
        retrieved_context=context,
        draft_response=run.draft_response,
        escalation_required=run.escalation_required,
        status=run.status,
    )


@router.get(
    "/agent/runs/{email_id}",
    response_model=AgentRunResponse | None,
)
def get_latest_agent_run(
    email_id: str,
    db: Session = Depends(get_database),
):
    service = AgentService(db)

    run = service.get_latest_run(email_id)

    if not run:
        return None

    context = []

    if run.retrieved_context:
        context = [
            item.strip()
            for item in run.retrieved_context.split("\n\n")
            if item.strip()
        ]

    return AgentRunResponse(
        run_id=run.id,
        email_id=run.email_id,
        intent=run.intent,
        confidence=run.confidence,
        retrieved_context=context,
        draft_response=run.draft_response,
        escalation_required=run.escalation_required,
        status=run.status,
    )