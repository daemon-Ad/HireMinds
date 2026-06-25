from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.candidate import CandidateResponse, CandidateWithScoreResponse
from app.services import candidate_service
from app.db.database import get_db
from app.dependencies import get_current_recruiter
from app.models.recruiter import Recruiter
from app.utils import pdf_parser

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("/upload", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
def upload_candidate(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_recruiter: Recruiter = Depends(get_current_recruiter),
):
    """
    Upload a candidate CV (PDF).
    - Text is extracted from the PDF here in the router.
    - CVParserAgent parses the text into structured fields.
    - Matching against all of this recruiter's JDs is triggered automatically.
    Returns 409 if a candidate with the same email already exists.
    Returns 422 if the PDF yields no text or no email can be parsed.
    """
    raw_bytes = file.file.read()
    if not raw_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    raw_text = pdf_parser.extract_text(raw_bytes)

    return candidate_service.create_candidate(
        db=db,
        raw_cv_text=raw_text,
        recruiter_id=current_recruiter.recruiter_id,
    )


@router.get("/", response_model=List[CandidateResponse])
def list_candidates(
    db: Session = Depends(get_db),
    current_recruiter: Recruiter = Depends(get_current_recruiter),
):
    """
    List all candidates that have been matched against this recruiter's JDs.
    Deduplicates candidates who matched multiple JDs.
    """
    return candidate_service.list_candidates(
        db=db,
        recruiter_id=current_recruiter.recruiter_id,
    )


@router.get("/{jd_id}", response_model=List[CandidateWithScoreResponse])
def get_candidates_for_jd(
    jd_id: UUID,
    db: Session = Depends(get_db),
    current_recruiter: Recruiter = Depends(get_current_recruiter),
):
    """
    Return all candidates matched against a specific JD, ranked by
    overall_score DESC. Returns 404 if the JD doesn't exist or belongs
    to a different recruiter.
    """
    return candidate_service.get_ranked_candidates(
        db=db,
        jd_id=jd_id,
        recruiter_id=current_recruiter.recruiter_id,
    )
