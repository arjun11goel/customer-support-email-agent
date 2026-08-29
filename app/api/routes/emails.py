from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_database
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
    service = EmailService(db)

    return service.create_mock_email(data)


@router.get(
    "/emails",
    response_model=list[EmailResponse],
)
def list_emails(
    db: Session = Depends(get_database),
):
    service = EmailService(db)

    return service.list_emails()


@router.get(
    "/emails/{email_id}",
    response_model=EmailResponse,
)
def get_email(
    email_id: str,
    db: Session = Depends(get_database),
):
    service = EmailService(db)

    return service.get_email(email_id)