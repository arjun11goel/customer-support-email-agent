from app.database.init_db import initialize_database
from app.database.connection import SessionLocal
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


def main():
    initialize_database()

    db = SessionLocal()

    try:
        service = EmailService(db)

        for item in MOCK_EMAILS:
            email = service.create_mock_email(
                MockEmailCreate(**item)
            )

            print(
                f"Created email: "
                f"{email.id} | {email.subject}"
            )
    finally:
        db.close()


if __name__ == "__main__":
    main()