from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    sender_email: Optional[EmailStr] = None   # The From: address for interview emails


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class RecruiterProfileResponse(BaseModel):
    recruiter_id: UUID   # UUID type — FastAPI serializes it to string in JSON
    username: str
    email: str
    sender_email: Optional[str] = None

    class Config:
        from_attributes = True


class UpdateSenderEmailRequest(BaseModel):
    sender_email: EmailStr


