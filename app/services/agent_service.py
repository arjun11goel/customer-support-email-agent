import json

from sqlalchemy.orm import Session

from app.ai.workflow.graph import agent_graph
from app.ai.workflow.state import AgentState
from app.core.exceptions import AgentRunException
from app.models.agent_run import AgentRun
from app.repositories.agent_repository import AgentRepository
from app.services.email_service import EmailService
from app.services.response_service import ResponseService


class AgentService:
    """Business logic for executing and saving agent runs."""

    def __init__(self, db: Session):
        self.db = db
        self.agent_repository = AgentRepository(db)
        self.email_service = EmailService(db)
        self.response_service = ResponseService(db)

    def run(self, email_id: str) -> AgentRun:
        """Run the workflow, save its result, and update the inbox status."""
        email = self.email_service.get_email(email_id)

        state: AgentState = {
            "email_id": email.id,
            "sender": email.sender,
            "recipient": email.recipient,
            "subject": email.subject,
            "body": email.body,
            "status": "started",
        }

        try:
            result = agent_graph.invoke(state)
        except Exception as exc:
            raise AgentRunException(
                f"Agent execution failed: {exc}"
            ) from exc

        agent_run = AgentRun(
            email_id=email.id,
            intent=result.get("intent"),
            confidence=result.get("confidence"),
            retrieved_context="\n\n".join(
                result.get("retrieved_context", [])
            ),
            draft_response=result.get("draft_response"),
            grounding_score=result.get("grounding_score"),
            validation_passed=result.get("validation_passed"),
            validation_issues=json.dumps(
                result.get("validation_issues", [])
            ),
            review_required=result.get("review_required", True),
            escalation_required=result.get(
                "escalation_required",
                False,
            ),
            escalation_reasons=json.dumps(
                result.get("escalation_reasons", [])
            ),
            error=result.get("error"),
            status=result.get("status", "completed"),
        )

        saved_run = self.agent_repository.create(agent_run)

        if saved_run.draft_response:
            saved_response = self.response_service.create_draft(
                email_id=saved_run.email_id,
                agent_run_id=saved_run.id,
                content=saved_run.draft_response,
            )

            if result.get("auto_send_eligible", False):
                self.response_service.auto_send_demo(saved_response.id)

        inbox_status = (
            "escalated"
            if saved_run.escalation_required
            else "needs_review"
            if saved_run.review_required
            else "processed"
        )
        self.email_service.update_status(email.id, inbox_status)

        return saved_run

    def get_latest_run(self, email_id: str) -> AgentRun | None:
        """Return the newest saved run for an email."""
        return self.agent_repository.get_latest_for_email(email_id)