from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session

from app.models.recruiter import Recruiter


def get_by_id(db: Session, recruiter_id: UUID) -> Optional[Recruiter]:
    return db.query(Recruiter).filter(
        Recruiter.recruiter_id == recruiter_id
    ).first()


def get_by_email(db: Session, email: str) -> Optional[Recruiter]:
    return db.query(Recruiter).filter(
        Recruiter.email == email
    ).first()


def create(
    db: Session,
    username: str,
    email: str,
    password_hash: str,
    sender_email: Optional[str] = None,
) -> Recruiter:
    recruiter = Recruiter(
        username=username,
        email=email,
        password_hash=password_hash,
        sender_email=sender_email,
    )
    db.add(recruiter)
    db.flush()
    db.refresh(recruiter)
    return recruiter


def update_sender_email(
    db: Session,
    recruiter_id: UUID,
    sender_email: str,
) -> Recruiter:
    """Update the From: address used in interview emails for this recruiter."""
    recruiter = get_by_id(db=db, recruiter_id=recruiter_id)
    recruiter.sender_email = sender_email
    db.flush()
    db.refresh(recruiter)
    return recruiter

