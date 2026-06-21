from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
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
    )

    access_token = jwt_handler.create_access_token(subject=str(recruiter.recruiter_id))
    return TokenResponse(access_token=access_token, token_type="bearer")


def login(db: Session, request: LoginRequest) -> TokenResponse:
    recruiter = recruiter_repo.get_by_email(db=db, email=request.email)
    if not recruiter:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )

    if not password_hasher.verify_password(request.password, recruiter.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )

    access_token = jwt_handler.create_access_token(subject=str(recruiter.recruiter_id))
    return TokenResponse(access_token=access_token, token_type="bearer")
