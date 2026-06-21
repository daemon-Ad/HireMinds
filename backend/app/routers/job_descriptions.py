from uuid import UUID
from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session

from app.schemas.job_description import JDCreateRequest, JDResponse, JDListResponse
from app.services import jd_service
from app.db.database import get_db
from app.dependencies import get_current_recruiter
from app.models.recruiter import Recruiter

router = APIRouter(prefix="/jd", tags=["job_descriptions"])


@router.post("/upload", response_model=JDResponse, status_code=status.HTTP_201_CREATED)
def upload_jd(
    request: JDCreateRequest,
    db: Session = Depends(get_db),
    current_recruiter: Recruiter = Depends(get_current_recruiter),
):
    return jd_service.create_jd(db=db, request=request, recruiter_id=current_recruiter.recruiter_id)


@router.get("/", response_model=JDListResponse)
def list_jds(
        db: Session = Depends(get_db),
        current_recruiter: Recruiter = Depends(get_current_recruiter),
):
    return jd_service.list_jds(db=db, recruiter_id=current_recruiter.recruiter_id)


@router.get("/{jd_id}", response_model=JDResponse)
def get_jd(jd_id: UUID, db: Session = Depends(get_db)):
    return jd_service.get_jd(db=db, jd_id=jd_id)
