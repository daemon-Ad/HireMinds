import json
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.config import settings
from app.schemas.match import MatchResponse, ShortlistResponse
from app.db.repositories import candidate_repo, jd_repo, match_repo
from app.agents.matching_engine import MatchingEngineAgent
from app.agents.jd_summarizer import ParsedJD
from app.agents.cv_parser import ParsedCandidate


def _orm_to_parsed_candidate(candidate) -> ParsedCandidate:
    """Convert a Candidate ORM instance to ParsedCandidate for the agent."""
    skills = []
    if candidate.skills:
        try:
            skills = json.loads(candidate.skills)
        except (ValueError, TypeError):
            skills = [s.strip() for s in candidate.skills.split(",") if s.strip()]

    experience_json = []
    if candidate.experience_json:
        try:
            experience_json = json.loads(candidate.experience_json)
        except (ValueError, TypeError):
            pass

    education_json = []
    if candidate.education_json:
        try:
            education_json = json.loads(candidate.education_json)
        except (ValueError, TypeError):
            pass

    return ParsedCandidate(
        name=candidate.name,
        email=candidate.email,
        phone=candidate.phone,
        skills=skills,
        experience_json=experience_json,
        education_json=education_json,
    )


def _orm_to_parsed_jd(jd) -> ParsedJD:
    """Convert a JobDescription ORM instance to ParsedJD for the agent."""
    required_skills = []
    if jd.required_skills:
        try:
            required_skills = json.loads(jd.required_skills)
        except (ValueError, TypeError):
            required_skills = [s.strip() for s in jd.required_skills.split(",") if s.strip()]

    responsibilities = []
    if jd.responsibilities:
        try:
            responsibilities = json.loads(jd.responsibilities)
        except (ValueError, TypeError):
            pass

    return ParsedJD(
        required_skills=required_skills,
        min_experience_years=jd.min_experience_years or 0,
        required_education=jd.required_education or "None",
        responsibilities=responsibilities,
    )


def run_match(db: Session, candidate_id: UUID, jd_id: UUID) -> MatchResponse:
    candidate = candidate_repo.get_by_id(db=db, candidate_id=candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate {candidate_id} not found.",
        )

    jd = jd_repo.get_by_id(db=db, jd_id=jd_id)
    if not jd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description {jd_id} not found.",
        )

    parsed_candidate = _orm_to_parsed_candidate(candidate)
    parsed_jd = _orm_to_parsed_jd(jd)

    engine = MatchingEngineAgent()
    result = engine.run(candidate=parsed_candidate, jd=parsed_jd)

    match = match_repo.create_or_update(
        db=db,
        candidate_id=candidate_id,
        jd_id=jd_id,
        recruiter_id=jd.recruiter_id,
        skill_score=result.skill_score,
        experience_score=result.experience_score,
        education_score=result.education_score,
        keyword_score=result.keyword_score,
        overall_score=result.overall_score,
        is_shortlisted=result.is_shortlisted,
    )

    return MatchResponse.model_validate(match)


def get_matches_for_jd(
    db: Session, jd_id: UUID, recruiter_id: UUID
) -> List[MatchResponse]:
    """Return all match records for a JD, ordered by overall_score DESC."""
    jd = jd_repo.get_by_id(db=db, jd_id=jd_id)
    if not jd or jd.recruiter_id != recruiter_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description {jd_id} not found.",
        )

    matches = match_repo.get_by_jd_id(db=db, jd_id=jd_id)
    return [MatchResponse.model_validate(m) for m in matches]


def get_shortlisted(
    db: Session, jd_id: UUID, recruiter_id: UUID
) -> List[MatchResponse]:
    """Return only shortlisted match records for a JD, ordered by overall_score DESC."""
    jd = jd_repo.get_by_id(db=db, jd_id=jd_id)
    if not jd or jd.recruiter_id != recruiter_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description {jd_id} not found.",
        )

    matches = match_repo.get_shortlisted_by_jd_id(db=db, jd_id=jd_id)
    return [MatchResponse.model_validate(m) for m in matches]
