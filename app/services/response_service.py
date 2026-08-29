from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.response import Response
from app.repositories.response_repository import ResponseRepository


class ResponseService:
    """Business logic for generated customer responses."""

    def __init__(self, db: Session):
        self.repository = ResponseRepository(db)

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

    def approve(
        self,
        response_id: str,
        approved_by: str,
    ) -> Response:
        response = self.repository.get_by_id(response_id)

        if not response:
            raise ValueError(
                f"Response '{response_id}' not found."
            )

        response.status = "approved"
        response.approved_by = approved_by

        return self.repository.update(response)

    def send(
        self,
        response_id: str,
    ) -> Response:
        response = self.repository.get_by_id(response_id)

        if not response:
            raise ValueError(
                f"Response '{response_id}' not found."
            )

        response.status = "sent"
        response.sent_at = datetime.now(timezone.utc)

        return self.repository.update(response)