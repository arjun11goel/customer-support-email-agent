from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    """Credentials submitted by the demo user."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    """Public user details returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    company_name: str
    role: str


class LoginResponse(BaseModel):
    """Access token and account details returned after login."""

    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user: UserResponse