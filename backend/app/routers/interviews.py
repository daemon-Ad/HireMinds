from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.interview import InterviewTriggerRequest, InterviewResponse
from app.services import interview_service
from app.db.database import get_db
from app.dependencies import get_current_recruiter
from app.models.recruiter import Recruiter

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("/send", response_model=List[InterviewResponse], status_code=status.HTTP_201_CREATED)
def send_interviews(
    request: InterviewTriggerRequest,
    db: Session = Depends(get_db),
    current_recruiter: Recruiter = Depends(get_current_recruiter),
):
    """
    Trigger interview invitation emails for all shortlisted candidates on a JD.
    - proposed_slots: list of human-readable time slot strings included in each email.
    - Each shortlisted candidate gets a personalised email via Groq LLaMA.
    - Re-triggering overwrites previously generated emails (idempotent).
    Returns 404 if the JD doesn't exist, belongs to another recruiter,
    or has no shortlisted candidates.
    """
    return interview_service.send_interviews(
        db=db,
        jd_id=request.jd_id,
        proposed_slots=request.proposed_slots,
        recruiter_id=current_recruiter.recruiter_id,
    )


@router.get("/", response_model=List[InterviewResponse])
def list_interviews(
    db: Session = Depends(get_db),
    current_recruiter: Recruiter = Depends(get_current_recruiter),
):
    """
    List all interview invitations sent by the authenticated recruiter,
    ordered by sent_at DESC.
    """
    return interview_service.list_interviews(
        db=db,
        recruiter_id=current_recruiter.recruiter_id,
    )
