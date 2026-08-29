from app.schemas.common import IntentCategory
from app.schemas.email import MockEmailCreate


def test_mock_email_schema():
    email = MockEmailCreate(
        sender="customer@example.com",
        recipient="support@example.com",
        subject="Billing issue",
        body="I was charged twice.",
    )

    assert email.sender == "customer@example.com"
    assert email.subject == "Billing issue"


def test_intent_categories():
    assert (
        IntentCategory.BILLING_ISSUE.value
        == "billing_issue"
    )