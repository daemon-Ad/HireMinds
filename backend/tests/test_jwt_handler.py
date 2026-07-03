import time
import uuid
import pytest
from uuid import UUID


def test_create_token_returns_string():
    from app.utils.jwt_handler import create_access_token
    token = create_access_token(subject=str(uuid.uuid4()))
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_token_round_trips_subject():
    from app.utils.jwt_handler import create_access_token, decode_token
    recruiter_id = str(uuid.uuid4())
    token = create_access_token(subject=recruiter_id)
    decoded = decode_token(token)
    assert decoded == recruiter_id


def test_tampered_token_raises():
    from app.utils.jwt_handler import create_access_token, decode_token
    token = create_access_token(subject=str(uuid.uuid4()))
    tampered = token[:-5] + "XXXXX"
    with pytest.raises(Exception):
        decode_token(tampered)


def test_expired_token_raises():
    """Create a token that expires immediately and verify it raises."""
    import jwt as pyjwt
    from app.utils.jwt_handler import decode_token
    from app.config import settings
    from datetime import datetime, timedelta, timezone

    payload = {
        "sub": str(uuid.uuid4()),
        "exp": datetime.now(timezone.utc) - timedelta(seconds=1),  # already expired
    }
    expired_token = pyjwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    with pytest.raises(Exception):
        decode_token(expired_token)


def test_empty_string_raises():
    from app.utils.jwt_handler import decode_token
    with pytest.raises(Exception):
        decode_token("")


def test_garbage_string_raises():
    from app.utils.jwt_handler import decode_token
    with pytest.raises(Exception):
        decode_token("not.a.jwt")
