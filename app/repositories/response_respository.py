from sqlalchemy.orm import Session

from app.models.response import Response


class ResponseRepository:
    """Database operations for responses."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, response: Response) -> Response:
        self.db.add(response)
        self.db.commit()
        self.db.refresh(response)
        return response

    def get_by_id(
        self,
        response_id: str,
    ) -> Response | None:
        return (
            self.db.query(Response)
            .filter(Response.id == response_id)
            .first()
        )

    def update(self, response: Response) -> Response:
        self.db.commit()
        self.db.refresh(response)
        return response