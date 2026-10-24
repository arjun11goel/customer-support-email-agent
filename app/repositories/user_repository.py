from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Database operations for demo workspace users."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        """Find a user by email address, ignoring letter case."""
        normalized_email = email.strip().lower()

        return (
            self.db.query(User)
            .filter(User.email == normalized_email)
            .first()
        )

    def create(self, user: User) -> User:
        """Save a new user account."""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user