from sqlalchemy.orm import Session

from app.core.exceptions import EmailNotFoundException
from app.models.email import Email
from app.repositories.email_repository import EmailRepository
from app.schemas.email import MockEmailCreate


class EmailService:
    """Business logic for customer emails."""

    def __init__(self, db: Session):
        self.repository = EmailRepository(db)

    def create_mock_email(self, data: MockEmailCreate) -> Email:
        email = Email(
            sender=str(data.sender),
            recipient=str(data.recipient),
            subject=data.subject,
            body=data.body,
            source="mock",
            status="new",
        )
        return self.repository.create(email)

    def get_email(self, email_id: str) -> Email:
        email = self.repository.get_by_id(email_id)

        if not email:
            raise EmailNotFoundException(email_id)

        return email

    def list_emails(self) -> list[Email]:
        return self.repository.list_all()

    def update_status(self, email_id: str, status: str) -> Email:
        """Update an email's inbox status."""
        email = self.get_email(email_id)
        return self.repository.update_status(email, status)