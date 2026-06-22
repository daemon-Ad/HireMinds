from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.schemas.auth import RegisterRequest, TokenResponse
from app.services import auth_service
from app.db.database import get_db

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
