from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.schemas.auth import RegisterRequest, TokenResponse, RecruiterProfileResponse
from app.db.repositories import recruiter_repo
from app.utils import password_hasher, jwt_handler


def register(db: Session, request: RegisterRequest) -> TokenResponse:
    existing = recruiter_repo.get_by_email(db=db, email=request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A recruiter with this email already exists.",
        )

    hashed = password_hasher.hash_password(request.password)
    recruiter = recruiter_repo.create(
        db=db,
        username=request.username,
        email=request.email,
        password_hash=hashed,
        sender_email=str(request.sender_email) if request.sender_email else None,
    )

    access_token = jwt_handler.create_access_token(subject=str(recruiter.recruiter_id))
    return TokenResponse(access_token=access_token, token_type="bearer")


def login(db: Session, email: str, password: str) -> TokenResponse:
    recruiter = recruiter_repo.get_by_email(db=db, email=email)
    if not recruiter:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )

    if not password_hasher.verify_password(password, recruiter.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )

    access_token = jwt_handler.create_access_token(subject=str(recruiter.recruiter_id))
    return TokenResponse(access_token=access_token, token_type="bearer")


def get_profile(db: Session, recruiter_id: UUID) -> RecruiterProfileResponse:
    """Return the authenticated recruiter's profile including sender_email."""
    recruiter = recruiter_repo.get_by_id(db=db, recruiter_id=recruiter_id)
    return RecruiterProfileResponse.model_validate(recruiter)


def update_sender_email(
    db: Session,
    recruiter_id: UUID,
    sender_email: str,
) -> RecruiterProfileResponse:
    """Update the From: address used in interview emails for this recruiter."""
    recruiter = recruiter_repo.update_sender_email(
        db=db,
        recruiter_id=recruiter_id,
        sender_email=sender_email,
    )
    return RecruiterProfileResponse.model_validate(recruiter)

