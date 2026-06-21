import logging
from datetime import datetime, timedelta, timezone

import jwt  # PyJWT

from app.config import settings

logger = logging.getLogger(__name__)

_SECRET_KEY: str = settings.SECRET_KEY
_ALGORITHM: str = settings.JWT_ALGORITHM
_EXPIRE_MINUTES: int = settings.JWT_EXPIRE_MINUTES


def create_access_token(subject: str) -> str:
    """
    Create a signed JWT access token encoding the subject (recruiter_id).

    Args:
        subject: String representation of the recruiter_id UUID.

    Returns:
        A signed JWT string.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=_EXPIRE_MINUTES)
    payload = {
        "sub": subject,
        "exp": expire,
    }
    return jwt.encode(payload, _SECRET_KEY, algorithm=_ALGORITHM)


def decode_token(token: str) -> str:
    """
    Decode and validate a JWT token, returning the recruiter_id (subject).

    Args:
        token: The raw JWT string.

    Returns:
        The recruiter_id string stored in the 'sub' claim.

    Raises:
        jwt.ExpiredSignatureError: If the token has expired.
        jwt.InvalidTokenError:     If the token is malformed or signature is invalid.
    """
    payload = jwt.decode(token, _SECRET_KEY, algorithms=[_ALGORITHM])
    return payload["sub"]
