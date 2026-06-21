from uuid import UUID
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.candidate import Candidate


def get_by_id(db: Session, candidate_id: UUID) -> Optional[Candidate]:
    return db.query(Candidate).filter(
        Candidate.candidate_id == candidate_id
    ).first()


def get_by_email(db: Session, email: str) -> Optional[Candidate]:
    return db.query(Candidate).filter(
        Candidate.email == email
    ).first()


def get_all(db: Session) -> List[Candidate]:
    return db.query(Candidate).all()


def create(
    db: Session,
    name: str,
    email: str,
    raw_cv_text: str,
    phone: Optional[str] = None,
    skills: Optional[str] = None,
    experience_json: Optional[str] = None,
    education_json: Optional[str] = None,
) -> Candidate:
    candidate = Candidate(
        name=name,
        email=email,
        phone=phone,
        skills=skills,
        experience_json=experience_json,
        education_json=education_json,
        raw_cv_text=raw_cv_text,
    )
    db.add(candidate)
    db.flush()
    db.refresh(candidate)
    return candidate
