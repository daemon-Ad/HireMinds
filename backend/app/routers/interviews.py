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
def send_interview(
    request: InterviewTriggerRequest,
    db: Session = Depends(get_db),
    current_recruiter: Recruiter = Depends(get_current_recruiter),
):
    return interview_service.send_interview(db=db, request=request)


@router.get("/", response_model=List[InterviewResponse])
def list_interviews(
    db: Session = Depends(get_db),
    current_recruiter: Recruiter = Depends(get_current_recruiter),
):
    return interview_service.list_interviews(db=db)
