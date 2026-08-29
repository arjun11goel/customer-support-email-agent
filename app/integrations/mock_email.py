from app.integrations.base import EmailProvider


class MockEmailProvider(EmailProvider):
    """Mock provider used during local development."""

    def fetch_emails(self) -> list[dict]:
        return []

    def get_email(self, email_id: str) -> dict:
        raise NotImplementedError(
            "Mock email retrieval will be connected to the database."
        )

    def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
    ) -> dict:
        return {
            "provider": "mock",
            "status": "sent",
            "recipient": recipient,
            "subject": subject,
        }