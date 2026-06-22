import json
from uuid import UUID
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.schemas.candidate import CandidateResponse, CandidateWithScoreResponse
from app.db.repositories import candidate_repo, match_repo
from app.agents.cv_parser import CVParserAgent
from app.services import orchestrator


def create_candidate(
    db: Session,
    raw_cv_text: str,
    recruiter_id: UUID,
) -> CandidateResponse:
    """
    Parse raw CV text, persist the candidate, and immediately trigger
    matching against all of this recruiter's JDs via the orchestrator.

    PDF extraction is done upstream in the router before calling here.
    """
    if not raw_cv_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract any text from the uploaded CV.",
        )

    parser = CVParserAgent()
    parsed = parser.run(raw_cv_text=raw_cv_text)

    # Guard: email is required for uniqueness; use a fallback if extraction missed it
    if not parsed.email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract a valid email address from the CV.",
        )

    # If candidate already exists by email, reuse them and re-run matching
    # against this recruiter's JDs (candidate can apply to multiple roles)
    existing = candidate_repo.get_by_email(db=db, email=parsed.email)
    if existing:
        orchestrator.run_matching_pipeline(
            db=db,
            candidate_id=existing.candidate_id,
            recruiter_id=recruiter_id,
        )
        return CandidateResponse.model_validate(existing)

    candidate = candidate_repo.create(
        db=db,
        name=parsed.name,
        email=parsed.email,
        phone=parsed.phone,
        skills=json.dumps(parsed.skills),
        experience_json=json.dumps(parsed.experience_json),
        education_json=json.dumps(parsed.education_json),
        raw_cv_text=raw_cv_text,
    )

    # Trigger matching against all of this recruiter's JDs
    orchestrator.run_matching_pipeline(
        db=db,
        candidate_id=candidate.candidate_id,
        recruiter_id=recruiter_id,
    )

    return CandidateResponse.model_validate(candidate)


def list_candidates(db: Session, recruiter_id: UUID) -> List[CandidateResponse]:
    """
    Return all candidates that have at least one match record against
    this recruiter's JDs — i.e. candidates this recruiter has uploaded CVs for.
    """
    matches = match_repo.get_by_recruiter_id(db=db, recruiter_id=recruiter_id)
    # Deduplicate — a candidate may match multiple JDs of the same recruiter
    seen = set()
    candidates = []
    for match in matches:
        candidate = match.candidate
        if candidate.candidate_id not in seen:
            seen.add(candidate.candidate_id)
            candidates.append(CandidateResponse.model_validate(candidate))
    return candidates


def get_ranked_candidates(
    db: Session,
    jd_id: UUID,
    recruiter_id: UUID,
) -> List[CandidateWithScoreResponse]:
    """
    Return all candidates matched against the given JD, ordered by
    overall_score DESC. Validates JD ownership before returning data.
    """
    from app.db.repositories import jd_repo
    jd = jd_repo.get_by_id(db=db, jd_id=jd_id)
    if not jd or jd.recruiter_id != recruiter_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description {jd_id} not found.",
        )

    matches = match_repo.get_by_jd_id(db=db, jd_id=jd_id)
    if not matches:
        return []

    results = []
    for match in matches:
        candidate = match.candidate
        results.append(
            CandidateWithScoreResponse(
                candidate_id=candidate.candidate_id,
                name=candidate.name,
                email=candidate.email,
                phone=candidate.phone,
                skills=candidate.skills,
                experience_json=candidate.experience_json,
                education_json=candidate.education_json,
                raw_cv_text=candidate.raw_cv_text,
                created_at=candidate.created_at,
                overall_score=match.overall_score,
                skill_score=match.skill_score,
                experience_score=match.experience_score,
                education_score=match.education_score,
                keyword_score=match.keyword_score,
                is_shortlisted=match.is_shortlisted,
            )
        )
    # match_repo.get_by_jd_id already orders by overall_score DESC
    return results
