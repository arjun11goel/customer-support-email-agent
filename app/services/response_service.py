from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.response import Response
from app.repositories.response_repository import ResponseRepository
from app.services.email_service import EmailService


class ResponseService:
    """Business logic for generated customer responses."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = ResponseRepository(db)
        self.email_service = EmailService(db)

    def create_draft(
        self,
        email_id: str,
        agent_run_id: str,
        content: str,
    ) -> Response:
        response = Response(
            email_id=email_id,
            agent_run_id=agent_run_id,
            content=content,
            status="draft",
        )
        return self.repository.create(response)

    def get_by_id(self, response_id: str) -> Response | None:
        """Find one response by ID."""
        return self.repository.get_by_id(response_id)

    def get_for_agent_run(
        self,
        agent_run_id: str,
    ) -> Response | None:
        """Return the latest saved response for an agent run."""
        return self.repository.get_latest_for_agent_run(agent_run_id)

    def update_draft(
        self,
        response_id: str,
        content: str,
    ) -> Response:
        """Save an edited response while it is still a draft."""
        response = self.get_by_id(response_id)

        if not response:
            raise ValueError(f"Response '{response_id}' not found.")

        if response.status != "draft":
            raise ValueError("Only a draft response can be edited.")

        cleaned_content = content.strip()

        if not cleaned_content:
            raise ValueError("The response draft cannot be empty.")

        response.content = cleaned_content
        return self.repository.update(response)

    def approve(
        self,
        response_id: str,
        approved_by: str,
    ) -> Response:
        """Record approval of a draft."""
        response = self.get_by_id(response_id)

        if not response:
            raise ValueError(f"Response '{response_id}' not found.")

        if response.status not in {"draft", "approved"}:
            raise ValueError("Only a draft can be approved.")

        response.status = "approved"
        response.approved_by = approved_by
        return self.repository.update(response)

    def send(self, response_id: str) -> Response:
        """Record a demo send in the database; no email is sent."""
        response = self.get_by_id(response_id)

        if not response:
            raise ValueError(f"Response '{response_id}' not found.")

        if response.status != "approved":
            raise ValueError("Approve the response before marking it sent.")

        response.status = "sent_demo"
        response.sent_at = datetime.now(timezone.utc)
        saved_response = self.repository.update(response)

        self.email_service.update_status(
            saved_response.email_id,
            "processed",
        )

        return saved_response

    def auto_send_demo(self, response_id: str) -> Response:
        """Approve and mark an eligible response as sent in the demo."""
        if not settings.AUTO_SEND_ENABLED:
            raise ValueError("Simulated auto-send is disabled.")

        approved_response = self.approve(
            response_id=response_id,
            approved_by="SupportFlow AI (simulated auto-send)",
        )

        return self.send(approved_response.id)