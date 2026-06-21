import json
from uuid import UUID
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile

from app.schemas.candidate import CandidateResponse, CandidateWithScoreResponse
from app.db.repositories import candidate_repo, match_repo
from app.agents.cv_parser import CVParserAgent
from app.utils import pdf_parser
from app.services import orchestrator


def upload_candidate(db: Session, file: UploadFile) -> CandidateResponse:
    raw_bytes = file.file.read()
    raw_text = pdf_parser.extract_text(raw_bytes)

    parser = CVParserAgent()
    parsed = parser.run(raw_cv_text=raw_text)

    candidate = candidate_repo.create(
        db=db,
        name=parsed.name,
        email=parsed.email,
        phone=parsed.phone,
        skills=json.dumps(parsed.skills),
        experience_json=json.dumps(parsed.experience_json),
        education_json=json.dumps(parsed.education_json),
        raw_cv_text=raw_text,
    )

    # Immediately trigger matching against all JDs in the system
    orchestrator.run_matching_pipeline(db=db, candidate_id=candidate.candidate_id)

    return CandidateResponse.model_validate(candidate)


def list_candidates(db: Session) -> List[CandidateResponse]:
    candidates = candidate_repo.get_all(db=db)
    return [CandidateResponse.model_validate(c) for c in candidates]


def get_ranked_candidates(db: Session, jd_id: UUID) -> List[CandidateWithScoreResponse]:
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

    return results
