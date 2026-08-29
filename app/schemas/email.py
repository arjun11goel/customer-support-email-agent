from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.common import EmailSource, EmailStatus


class MockEmailCreate(BaseModel):
    """Request for creating a mock customer email."""

    sender: EmailStr
    recipient: EmailStr
    subject: str = Field(min_length=1, max_length=500)
    body: str = Field(min_length=1)


class EmailResponse(BaseModel):
    """Email API response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    sender: str
    recipient: str
    subject: str
    body: str
    source: EmailSource
    status: EmailStatus
    received_at: datetime