from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.match import MatchResponse
from app.services import matching_service
from app.db.database import get_db
from app.dependencies import get_current_recruiter
from app.models.recruiter import Recruiter

router = APIRouter(prefix="/matches", tags=["matches"])


# ── IMPORTANT: /shortlisted/{jd_id} MUST be registered before /{jd_id} ────────
# FastAPI resolves routes top-to-bottom. If /{jd_id} were first, the literal
# string "shortlisted" would be captured as the UUID path param and raise 422.

@router.get("/shortlisted/{jd_id}", response_model=List[MatchResponse])
def get_shortlisted(
    jd_id: UUID,
    db: Session = Depends(get_db),
    current_recruiter: Recruiter = Depends(get_current_recruiter),
):
    """
    Return only shortlisted candidates for a JD (is_shortlisted=True),
    ordered by overall_score DESC.
    Returns 404 if the JD doesn't exist or belongs to a different recruiter.
    """
    return matching_service.get_shortlisted(
        db=db,
        jd_id=jd_id,
        recruiter_id=current_recruiter.recruiter_id,
    )


@router.get("/{jd_id}", response_model=List[MatchResponse])
def get_matches_for_jd(
    jd_id: UUID,
    db: Session = Depends(get_db),
    current_recruiter: Recruiter = Depends(get_current_recruiter),
):
    """
    Return all match records for a JD (shortlisted and non-shortlisted),
    ordered by overall_score DESC.
    Returns 404 if the JD doesn't exist or belongs to a different recruiter.
    """
    return matching_service.get_matches_for_jd(
        db=db,
        jd_id=jd_id,
        recruiter_id=current_recruiter.recruiter_id,
    )
