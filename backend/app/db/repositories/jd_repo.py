from uuid import UUID
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.job_description import JobDescription


def get_by_id(db: Session, jd_id: UUID) -> Optional[JobDescription]:
    return db.query(JobDescription).filter(
        JobDescription.jd_id == jd_id
    ).first()


def get_all(db: Session) -> List[JobDescription]:
    return db.query(JobDescription).all()


def get_by_recruiter(db: Session, recruiter_id: UUID) -> List[JobDescription]:
    return db.query(JobDescription).filter(
        JobDescription.recruiter_id == recruiter_id
    ).all()


def create(
    db: Session,
    title: str,
    raw_text: str,
    recruiter_id: UUID,
    required_skills: Optional[str] = None,
    min_experience_years: Optional[int] = None,
    required_education: Optional[str] = None,
    responsibilities: Optional[str] = None,
) -> JobDescription:
    jd = JobDescription(
        title=title,
        raw_text=raw_text,
        recruiter_id=recruiter_id,
        required_skills=required_skills,
        min_experience_years=min_experience_years,
        required_education=required_education,
        responsibilities=responsibilities,
    )
    db.add(jd)
    db.flush()
    db.refresh(jd)
    return jd
