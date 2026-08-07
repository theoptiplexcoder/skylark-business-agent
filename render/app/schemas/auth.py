from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    role: str
    avatar_url: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    theme_preference: str
    created_at: str

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    company: Optional[str] = None
    job_title: Optional[str] = None
    timezone: Optional[str] = None
    theme_preference: Optional[str] = None


class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
