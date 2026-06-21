from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.match import MatchResponse, ShortlistResponse
from app.services import matching_service
from app.db.database import get_db
from app.dependencies import get_current_recruiter
from app.models.recruiter import Recruiter

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("/{jd_id}", response_model=ShortlistResponse)
def get_matches(
    jd_id: UUID,
    db: Session = Depends(get_db),
    current_recruiter: Recruiter = Depends(get_current_recruiter),
):
    return matching_service.get_matches(db=db, jd_id=jd_id)


@router.get("/shortlisted/{jd_id}", response_model=ShortlistResponse)
def get_shortlisted(
    jd_id: UUID,
    db: Session = Depends(get_db),
    current_recruiter: Recruiter = Depends(get_current_recruiter),
):
    return matching_service.get_shortlisted(db=db, jd_id=jd_id)
