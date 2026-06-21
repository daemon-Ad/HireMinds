from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

import jwt

from app.utils import jwt_handler
from app.db.repositories import recruiter_repo
from app.db.database import get_db
from app.models.recruiter import Recruiter

_bearer = HTTPBearer()


def get_current_recruiter(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> Recruiter:
    """
    FastAPI dependency that decodes the Bearer JWT and returns the
    authenticated Recruiter ORM instance.

    Raises HTTP 401 if the token is missing, expired, or invalid.
    Raises HTTP 401 if the recruiter no longer exists in the database.

    Inject into protected routes with: Depends(get_current_recruiter)
    """
    token = credentials.credentials

    try:
        recruiter_id = jwt_handler.decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    recruiter = recruiter_repo.get_by_id(db=db, recruiter_id=recruiter_id)
    if not recruiter:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Recruiter not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return recruiter
