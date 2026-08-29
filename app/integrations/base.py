from abc import ABC, abstractmethod

from app.schemas.email import MockEmailCreate


class EmailProvider(ABC):
    """Common interface for all email providers."""

    @abstractmethod
    def fetch_emails(self) -> list[dict]:
        """Fetch incoming emails."""

    @abstractmethod
    def get_email(self, email_id: str) -> dict:
        """Get one email."""

    @abstractmethod
    def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
    ) -> dict:
        """Send an email."""