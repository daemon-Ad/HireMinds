from uuid import UUID
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.match import CandidateJDMatch


def get_by_id(db: Session, match_id: UUID) -> Optional[CandidateJDMatch]:
    return db.query(CandidateJDMatch).filter(
        CandidateJDMatch.match_id == match_id
    ).first()


def get_by_jd_and_candidate(db: Session, jd_id: UUID, candidate_id: UUID) -> Optional[CandidateJDMatch]:
    return db.query(CandidateJDMatch).filter(
        CandidateJDMatch.jd_id == jd_id,
        CandidateJDMatch.candidate_id == candidate_id
    ).first()


def get_by_jd_id(db: Session, jd_id: UUID) -> List[CandidateJDMatch]:
    return (
        db.query(CandidateJDMatch)
        .filter(CandidateJDMatch.jd_id == jd_id)
        .order_by(CandidateJDMatch.overall_score.desc())
        .all()
    )


def get_by_recruiter_id(db: Session, recruiter_id: UUID) -> List[CandidateJDMatch]:
    """Return all match records for a given recruiter, used to list their candidates."""
    return (
        db.query(CandidateJDMatch)
        .filter(CandidateJDMatch.recruiter_id == recruiter_id)
        .all()
    )


def get_shortlisted_by_jd_id(db: Session, jd_id: UUID) -> List[CandidateJDMatch]:
    return (
        db.query(CandidateJDMatch)
        .filter(
            CandidateJDMatch.jd_id == jd_id,
            CandidateJDMatch.is_shortlisted == True,
        )
        .order_by(CandidateJDMatch.overall_score.desc())
        .all()
    )


def create_or_update(
    db: Session,
    candidate_id: UUID,
    jd_id: UUID,
    recruiter_id: UUID,
    skill_score: Optional[float] = None,
    experience_score: Optional[float] = None,
    education_score: Optional[float] = None,
    keyword_score: Optional[float] = None,
    overall_score: Optional[float] = None,
    is_shortlisted: bool = False,
) -> CandidateJDMatch:
    existing = (
        db.query(CandidateJDMatch)
        .filter(
            CandidateJDMatch.candidate_id == candidate_id,
            CandidateJDMatch.jd_id == jd_id,
        )
        .first()
    )

    if existing:
        existing.skill_score = skill_score
        existing.experience_score = experience_score
        existing.education_score = education_score
        existing.keyword_score = keyword_score
        existing.overall_score = overall_score
        existing.is_shortlisted = is_shortlisted
        existing.matched_at = datetime.now(timezone.utc)
        db.flush()
        db.refresh(existing)
        return existing

    match = CandidateJDMatch(
        candidate_id=candidate_id,
        jd_id=jd_id,
        recruiter_id=recruiter_id,
        skill_score=skill_score,
        experience_score=experience_score,
        education_score=education_score,
        keyword_score=keyword_score,
        overall_score=overall_score,
        is_shortlisted=is_shortlisted,
        matched_at=datetime.now(timezone.utc),
    )
    db.add(match)
    db.flush()
    db.refresh(match)
    return match
