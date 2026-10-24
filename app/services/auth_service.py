from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.repositories.user_repository import UserRepository


password_hasher = PasswordHash.recommended()


class AuthService:
    """Business logic for the demo workspace login."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    def ensure_demo_user(self) -> User:
        """Create the demo account on first startup."""
        if not settings.DEMO_ADMIN_PASSWORD:
            raise ValueError(
                "Set DEMO_ADMIN_PASSWORD in the .env file."
            )

        if len(settings.DEMO_ADMIN_PASSWORD) < 8:
            raise ValueError(
                "DEMO_ADMIN_PASSWORD must contain at least 8 characters."
            )

        if not settings.JWT_SECRET_KEY:
            raise ValueError(
                "Set JWT_SECRET_KEY in the .env file."
            )

        email = settings.DEMO_ADMIN_EMAIL.strip().lower()
        user = self.user_repository.get_by_email(email)

        if user:
            return user

        user = User(
            email=email,
            password_hash=password_hasher.hash(
                settings.DEMO_ADMIN_PASSWORD
            ),
            company_name=settings.DEMO_COMPANY_NAME,
            role="support_admin",
            is_active=True,
        )

        return self.user_repository.create(user)

    def authenticate(
        self,
        email: str,
        password: str,
    ) -> User | None:
        """Return the account when the email and password are correct."""
        user = self.user_repository.get_by_email(email)

        if not user or not user.is_active:
            return None

        if not password_hasher.verify(password, user.password_hash):
            return None

        return user

    def create_access_token(self, user: User) -> tuple[str, int]:
        """Create a signed token that expires after the configured time."""
        if not settings.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY is not configured.")

        expires_in_seconds = (
            settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        expiration_time = datetime.now(timezone.utc) + timedelta(
            seconds=expires_in_seconds
        )

        token = jwt.encode(
            {
                "sub": user.id,
                "exp": expiration_time,
            },
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

        return token, expires_in_seconds