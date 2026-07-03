from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.schemas.auth import (
    RegisterRequest, TokenResponse,
    RecruiterProfileResponse, UpdateSenderEmailRequest,
)
from app.services import auth_service
from app.db.database import get_db
from app.dependencies import get_current_recruiter
from app.models.recruiter import Recruiter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new recruiter account.
    Returns a Bearer JWT token on success.
    Raises 409 if the email is already registered.
    """
    return auth_service.register(db=db, request=request)


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate a recruiter using email + password.
    Uses OAuth2PasswordRequestForm (form-data) so Swagger's Authorize button works.
    NOTE: OAuth2PasswordRequestForm calls the email field 'username' by spec —
    pass your email address in the username field.
    Returns a Bearer JWT token on success.
    Raises 401 if credentials are invalid.
    """
    return auth_service.login(db=db, email=form_data.username, password=form_data.password)


@router.get("/me", response_model=RecruiterProfileResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_recruiter: Recruiter = Depends(get_current_recruiter),
):
    """Return the authenticated recruiter's profile, including their sender_email."""
    return auth_service.get_profile(db=db, recruiter_id=current_recruiter.recruiter_id)


@router.patch("/me/sender-email", response_model=RecruiterProfileResponse)
def update_sender_email(
    request: UpdateSenderEmailRequest,
    db: Session = Depends(get_db),
    current_recruiter: Recruiter = Depends(get_current_recruiter),
):
    """
    Update the From: email address used when sending interview invitations.
    This address appears in the candidate's inbox as the sender.
    """
    return auth_service.update_sender_email(
        db=db,
        recruiter_id=current_recruiter.recruiter_id,
        sender_email=str(request.sender_email),
    )

