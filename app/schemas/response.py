from datetime import datetime

from pydantic import BaseModel


class ResponseResponse(BaseModel):
    id: str
    email_id: str
    agent_run_id: str
    content: str
    status: str
    approved_by: str | None = None
    sent_at: datetime | None = None


class ApproveResponseRequest(BaseModel):
    approved_by: str = "support_agent"


class SendResponseRequest(BaseModel):
    sender: str = "support@supportflow.local"