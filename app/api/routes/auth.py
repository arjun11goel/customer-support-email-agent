from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_database
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    UserResponse,
)
from app.services.auth_service import AuthService


router = APIRouter()


@router.post(
    "/auth/login",
    response_model=LoginResponse,
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_database),
) -> LoginResponse:
    """Check the demo account credentials and return an access token."""
    auth_service = AuthService(db)
    user = auth_service.authenticate(
        email=str(data.email),
        password=data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password is incorrect.",
        )

    token, expires_in_seconds = auth_service.create_access_token(user)

    return LoginResponse(
        access_token=token,
        expires_in_seconds=expires_in_seconds,
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/auth/me",
    response_model=UserResponse,
)
def get_logged_in_user(
    user: User = Depends(get_current_user),
) -> User:
    """Return details for the account associated with the access token."""
    return user