from sqlalchemy.orm import Session

from app.ai.workflow.graph import agent_graph
from app.ai.workflow.state import AgentState
from app.core.exceptions import AgentRunException
from app.models.agent_run import AgentRun
from app.repositories.agent_repository import AgentRepository
from app.services.email_service import EmailService


class AgentService:
    """Business logic for agent execution."""

    def __init__(self, db: Session):
        self.db = db
        self.agent_repository = AgentRepository(db)
        self.email_service = EmailService(db)

    def run(self, email_id: str) -> AgentRun:
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
            escalation_required=result.get(
                "escalation_required",
                False,
            ),
            status=result.get(
                "status",
                "completed",
            ),
        )

        return self.agent_repository.create(agent_run)

    def get_latest_run(self, email_id: str) -> AgentRun | None:
        return self.agent_repository.get_latest_for_email(
            email_id
        )