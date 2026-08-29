from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_database
from app.schemas.response import (
    ApproveResponseRequest,
    ResponseResponse,
    SendResponseRequest,
)
from app.services.response_service import ResponseService

router = APIRouter()


@router.post(
    "/responses/{response_id}/approve",
    response_model=ResponseResponse,
)
def approve_response(
    response_id: str,
    data: ApproveResponseRequest,
    db: Session = Depends(get_database),
):
    service = ResponseService(db)

    return service.approve(
        response_id=response_id,
        approved_by=data.approved_by,
    )


@router.post(
    "/responses/{response_id}/send",
    response_model=ResponseResponse,
)
def send_response(
    response_id: str,
    data: SendResponseRequest,
    db: Session = Depends(get_database),
):
    service = ResponseService(db)

    # Real email provider integration will be added later.
    return service.send(response_id)