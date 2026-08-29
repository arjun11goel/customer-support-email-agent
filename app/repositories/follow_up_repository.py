from sqlalchemy.orm import Session

from app.models.follow_up import FollowUp


class FollowUpRepository:
    """Database operations for follow-ups."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, follow_up: FollowUp) -> FollowUp:
        self.db.add(follow_up)
        self.db.commit()
        self.db.refresh(follow_up)
        return follow_up