from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_database
from app.schemas.response import (
    ApproveResponseRequest,
    ResponseResponse,
    UpdateResponseRequest,
)
from app.services.response_service import ResponseService


router = APIRouter()


@router.get(
    "/responses/{response_id}",
    response_model=ResponseResponse,
)
def get_response(
    response_id: str,
    db: Session = Depends(get_database),
):
    """Get a saved response and its current review status."""
    response = ResponseService(db).get_by_id(response_id)

    if not response:
        raise HTTPException(
            status_code=404,
            detail=f"Response '{response_id}' was not found.",
        )

    return response


@router.put(
    "/responses/{response_id}",
    response_model=ResponseResponse,
)
def update_response(
    response_id: str,
    data: UpdateResponseRequest,
    db: Session = Depends(get_database),
):
    """Save an edited response draft."""
    try:
        return ResponseService(db).update_draft(
            response_id=response_id,
            content=data.content,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post(
    "/responses/{response_id}/approve",
    response_model=ResponseResponse,
)
def approve_response(
    response_id: str,
    data: ApproveResponseRequest,
    db: Session = Depends(get_database),
):
    """Approve a response draft for the demo workflow."""
    try:
        return ResponseService(db).approve(
            response_id=response_id,
            approved_by=data.approved_by,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post(
    "/responses/{response_id}/send",
    response_model=ResponseResponse,
)
def send_response(
    response_id: str,
    db: Session = Depends(get_database),
):
    """Mark an approved response as sent in the demo database."""
    try:
        return ResponseService(db).send(response_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc