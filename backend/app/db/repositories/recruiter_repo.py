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


def create(db: Session, username: str, email: str, password_hash: str) -> Recruiter:
    recruiter = Recruiter(
        username=username,
        email=email,
        password_hash=password_hash,
    )
    db.add(recruiter)
    db.flush()
    db.refresh(recruiter)
    return recruiter
