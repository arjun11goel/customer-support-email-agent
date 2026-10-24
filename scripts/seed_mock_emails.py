from app.database.connection import SessionLocal
from app.database.init_db import initialize_database
from app.schemas.email import MockEmailCreate
from app.services.email_service import EmailService


MOCK_EMAILS = [
    {
        "sender": "john@example.com",
        "recipient": "support@example.com",
        "subject": "I was charged twice",
        "body": (
            "I was charged twice for my subscription. "
            "Can you please check this?"
        ),
    },
    {
        "sender": "sarah@example.com",
        "recipient": "support@example.com",
        "subject": "Dashboard is crashing",
        "body": (
            "The dashboard crashes whenever I upload a CSV file."
        ),
    },
    {
        "sender": "alex@example.com",
        "recipient": "support@example.com",
        "subject": "Do you support API access?",
        "body": (
            "I would like to know whether the current plan "
            "supports API access."
        ),
    },
]


def main() -> None:
    """Create sample emails without adding duplicates."""
    initialize_database()
    db = SessionLocal()

    try:
        service = EmailService(db)
        existing_pairs = {
            (email.sender.lower(), email.subject.lower())
            for email in service.list_emails()
        }

        created_count = 0

        for item in MOCK_EMAILS:
            pair = (item["sender"].lower(), item["subject"].lower())

            if pair in existing_pairs:
                continue

            email = service.create_mock_email(
                MockEmailCreate(**item)
            )
            existing_pairs.add(pair)
            created_count += 1
            print(f"Created email: {email.id} | {email.subject}")

        print(f"Added {created_count} new sample emails.")

    finally:
        db.close()


if __name__ == "__main__":
    main()