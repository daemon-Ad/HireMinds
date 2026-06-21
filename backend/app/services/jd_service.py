import json
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile

from app.schemas.job_description import JDCreateRequest, JDResponse, JDListResponse
from app.db.repositories import jd_repo
from app.agents.jd_summarizer import JDSummarizerAgent
from app.utils import pdf_parser


def create_jd(db: Session, request: JDCreateRequest, recruiter_id: UUID) -> JDResponse:
    summarizer = JDSummarizerAgent()
    parsed = summarizer.run(title=request.title, raw_text=request.raw_text)

    jd = jd_repo.create(
        db=db,
        title=request.title,
        raw_text=request.raw_text,
        recruiter_id=recruiter_id,
        required_skills=json.dumps(parsed.required_skills),
        min_experience_years=parsed.min_experience_years,
        required_education=parsed.required_education,
        responsibilities=json.dumps(parsed.responsibilities),
    )

    return JDResponse.model_validate(jd)


def create_jd_from_file(db: Session, file: UploadFile, recruiter_id: UUID) -> JDResponse:
    raw_bytes = file.file.read()
    raw_text = pdf_parser.extract_text(raw_bytes)
    title = file.filename or "Untitled"

    summarizer = JDSummarizerAgent()
    parsed = summarizer.run(title=title, raw_text=raw_text)

    jd = jd_repo.create(
        db=db,
        title=title,
        raw_text=raw_text,
        recruiter_id=recruiter_id,
        required_skills=json.dumps(parsed.required_skills),
        min_experience_years=parsed.min_experience_years,
        required_education=parsed.required_education,
        responsibilities=json.dumps(parsed.responsibilities),
    )

    return JDResponse.model_validate(jd)


def list_jds(db: Session, recruiter_id: UUID) -> JDListResponse:
    jds = jd_repo.get_by_recruiter(db=db, recruiter_id=recruiter_id)
    return JDListResponse(
        job_descriptions=[JDResponse.model_validate(jd) for jd in jds],
        total=len(jds),
    )


def get_jd(db: Session, jd_id: UUID) -> JDResponse:
    jd = jd_repo.get_by_id(db=db, jd_id=jd_id)
    if not jd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description {jd_id} not found.",
        )
    return JDResponse.model_validate(jd)
