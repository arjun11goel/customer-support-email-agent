from app.integrations.base import EmailProvider


class GmailProvider(EmailProvider):
    """Placeholder for future Gmail API integration."""

    def fetch_emails(self) -> list[dict]:
        raise NotImplementedError(
            "Gmail integration will be implemented later."
        )

    def get_email(self, email_id: str) -> dict:
        raise NotImplementedError(
            "Gmail integration will be implemented later."
        )

    def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
    ) -> dict:
        raise NotImplementedError(
            "Gmail integration will be implemented later."
        )