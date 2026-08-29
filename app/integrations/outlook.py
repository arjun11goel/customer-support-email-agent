from app.integrations.base import EmailProvider


class OutlookProvider(EmailProvider):
    """Placeholder for future Microsoft Graph integration."""

    def fetch_emails(self) -> list[dict]:
        raise NotImplementedError(
            "Outlook integration will be implemented later."
        )

    def get_email(self, email_id: str) -> dict:
        raise NotImplementedError(
            "Outlook integration will be implemented later."
        )

    def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
    ) -> dict:
        raise NotImplementedError(
            "Outlook integration will be implemented later."
        )