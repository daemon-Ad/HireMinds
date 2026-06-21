from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session

from app.schemas.candidate import CandidateResponse, CandidateWithScoreResponse
from app.services import candidate_service
from app.db.database import get_db
from app.dependencies import get_current_recruiter
from app.models.recruiter import Recruiter

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("/upload", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
def upload_candidate(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_recruiter: Recruiter = Depends(get_current_recruiter),
):
    return candidate_service.upload_candidate(db=db, file=file)


@router.get("/", response_model=List[CandidateResponse])
def list_candidates(
    db: Session = Depends(get_db),
    current_recruiter: Recruiter = Depends(get_current_recruiter),
):
    return candidate_service.list_candidates(db=db)


@router.get("/{jd_id}", response_model=List[CandidateWithScoreResponse])
def get_candidates_for_jd(
    jd_id: UUID,
    db: Session = Depends(get_db),
    current_recruiter: Recruiter = Depends(get_current_recruiter),
):
    return candidate_service.get_ranked_candidates(db=db, jd_id=jd_id)
