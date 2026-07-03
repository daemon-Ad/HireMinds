import json
import logging
from uuid import UUID
from typing import List
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks, HTTPException, status

from app.schemas.candidate import CandidateResponse, CandidateWithScoreResponse
from app.db.repositories import candidate_repo, match_repo
from app.agents.cv_parser import CVParserAgent
from app.services import orchestrator

logger = logging.getLogger(__name__)


def _run_matching_pipeline_bg(candidate_id: UUID, recruiter_id: UUID) -> None:
    """
    Background-safe wrapper for the matching pipeline.

    Opens its own DB session because FastAPI closes the request session before
    background tasks run — reusing the request session causes 'Session is closed'
    errors mid-pipeline.
    """
    from app.db.database import SessionLocal

    db = SessionLocal()
    try:
        orchestrator.run_matching_pipeline(
            db=db,
            candidate_id=candidate_id,
            recruiter_id=recruiter_id,
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error(
            "Background matching pipeline failed for candidate=%s — %s",
            candidate_id, exc,
        )
    finally:
        db.close()


def create_candidate(
    db: Session,
    raw_cv_text: str,
    recruiter_id: UUID,
    background_tasks: BackgroundTasks = None,
) -> CandidateResponse:
    """
    Parse raw CV text, persist the candidate, and schedule matching as a
    background task so the HTTP response returns immediately after parsing.

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
    if not parsed.email or parsed.email.lower() == "none" or "@" not in parsed.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file does not appear to be a valid CV (could not extract a valid email address).",
        )

    # We no longer enforce email uniqueness, allowing a candidate
    # to be uploaded multiple times for different roles or with updated CVs.

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

    # Schedule matching in the background — response returns immediately.
    # If no BackgroundTasks was provided (e.g. called from tests), run inline.
    if background_tasks is not None:
        background_tasks.add_task(
            _run_matching_pipeline_bg,
            candidate_id=candidate.candidate_id,
            recruiter_id=recruiter_id,
        )
        logger.info(
            "create_candidate: candidate=%s persisted, matching scheduled as background task",
            candidate.candidate_id,
        )
    else:
        orchestrator.run_matching_pipeline(
            db=db,
            candidate_id=candidate.candidate_id,
            recruiter_id=recruiter_id,
        )

    return CandidateResponse.model_validate(candidate)



def list_candidates(db: Session, recruiter_id: UUID) -> List[CandidateWithScoreResponse]:
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
            candidates.append(
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
    return candidates


def get_candidate_profile(db: Session, candidate_id: UUID, recruiter_id: UUID) -> CandidateResponse:
    """
    Return a candidate's profile if they are associated with the recruiter's JDs.
    """
    candidate = candidate_repo.get_by_id(db=db, candidate_id=candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate {candidate_id} not found."
        )

    # Validate that this recruiter has access to this candidate
    matches = match_repo.get_by_recruiter_id(db=db, recruiter_id=recruiter_id)
    if not any(match.candidate_id == candidate_id for match in matches):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this candidate."
        )

    return CandidateResponse.model_validate(candidate)



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
