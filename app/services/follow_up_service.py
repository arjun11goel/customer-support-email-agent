from datetime import datetime

from sqlalchemy.orm import Session

from app.models.follow_up import FollowUp
from app.repositories.follow_up_repository import FollowUpRepository


class FollowUpService:
    """Business logic for future follow-ups."""

    def __init__(self, db: Session):
        self.repository = FollowUpRepository(db)

    def schedule(
        self,
        email_id: str,
        scheduled_for: datetime,
        reason: str,
    ) -> FollowUp:
        follow_up = FollowUp(
            email_id=email_id,
            scheduled_for=scheduled_for,
            reason=reason,
            status="scheduled",
        )

        return self.repository.create(follow_up)