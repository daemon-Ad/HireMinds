from uuid import UUID
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.interview import Interview, InterviewStatus


def get_by_id(db: Session, interview_id: UUID) -> Optional[Interview]:
    return db.query(Interview).filter(
        Interview.interview_id == interview_id
    ).first()


def get_by_match_id(db: Session, match_id: UUID) -> Optional[Interview]:
    return db.query(Interview).filter(
        Interview.match_id == match_id
    ).first()


def get_all(db: Session) -> List[Interview]:
    return db.query(Interview).all()


def get_by_recruiter_id(db: Session, recruiter_id: UUID) -> List[Interview]:
    """Return all interviews belonging to the given recruiter, newest first."""
    return (
        db.query(Interview)
        .filter(Interview.recruiter_id == recruiter_id)
        .order_by(Interview.sent_at.desc())
        .all()
    )


def create_or_update(
    db: Session,
    match_id: UUID,
    recruiter_id: UUID,
    email_subject: Optional[str] = None,
    email_body: Optional[str] = None,
    proposed_slots: Optional[str] = None,
    status: str = "sent",
    sent_at: Optional[datetime] = None,
) -> Interview:
    existing = get_by_match_id(db=db, match_id=match_id)

    interview_status = InterviewStatus(status) if status in InterviewStatus._value2member_map_ else InterviewStatus.PENDING

    if existing:
        existing.email_subject = email_subject
        existing.email_body = email_body
        existing.proposed_slots = proposed_slots
        existing.status = interview_status
        existing.sent_at = sent_at
        db.flush()
        db.refresh(existing)
        return existing

    interview = Interview(
        match_id=match_id,
        recruiter_id=recruiter_id,
        email_subject=email_subject,
        email_body=email_body,
        proposed_slots=proposed_slots,
        status=interview_status,
        sent_at=sent_at,
    )
    db.add(interview)
    db.flush()
    db.refresh(interview)
    return interview
