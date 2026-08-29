from sqlalchemy.orm import Session

from app.models.agent_run import AgentRun


class AgentRepository:
    """Database operations for agent runs."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, agent_run: AgentRun) -> AgentRun:
        self.db.add(agent_run)
        self.db.commit()
        self.db.refresh(agent_run)
        return agent_run

    def get_by_id(self, run_id: str) -> AgentRun | None:
        return (
            self.db.query(AgentRun)
            .filter(AgentRun.id == run_id)
            .first()
        )

    def get_latest_for_email(
        self,
        email_id: str,
    ) -> AgentRun | None:
        return (
            self.db.query(AgentRun)
            .filter(AgentRun.email_id == email_id)
            .order_by(AgentRun.created_at.desc())
            .first()
        )