from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_database
from app.core.exceptions import EmailNotFoundException
from app.schemas.email import EmailResponse, MockEmailCreate
from app.services.email_service import EmailService

router = APIRouter()


@router.post(
    "/emails/mock",
    response_model=EmailResponse,
)
def create_mock_email(
    data: MockEmailCreate,
    db: Session = Depends(get_database),
):
    """Create a demo email in the inbox."""
    return EmailService(db).create_mock_email(data)


@router.get(
    "/emails",
    response_model=list[EmailResponse],
)
def list_emails(
    db: Session = Depends(get_database),
):
    """List emails, newest first."""
    return EmailService(db).list_emails()


@router.get(
    "/emails/{email_id}",
    response_model=EmailResponse,
)
def get_email(
    email_id: str,
    db: Session = Depends(get_database),
):
    """Get one email by ID."""
    try:
        return EmailService(db).get_email(email_id)
    except EmailNotFoundException as exc:
        raise HTTPException(
            status_code=404,
            detail=exc.message,
        ) from exc