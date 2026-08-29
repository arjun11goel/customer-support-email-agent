from sqlalchemy.orm import Session

from app.models.email import Email


class EmailRepository:
    """Database operations for customer emails."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, email: Email) -> Email:
        self.db.add(email)
        self.db.commit()
        self.db.refresh(email)
        return email

    def get_by_id(self, email_id: str) -> Email | None:
        return (
            self.db.query(Email)
            .filter(Email.id == email_id)
            .first()
        )

    def list_all(self) -> list[Email]:
        return (
            self.db.query(Email)
            .order_by(Email.received_at.desc())
            .all()
        )

    def update_status(
        self,
        email: Email,
        status: str,
    ) -> Email:
        email.status = status
        self.db.commit()
        self.db.refresh(email)
        return email