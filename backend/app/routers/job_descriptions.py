from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.schemas.job_description import JDCreateRequest, JDResponse, JDListResponse
from app.services import jd_service
from app.db.database import get_db
from app.dependencies import get_current_recruiter
from app.models.recruiter import Recruiter
from app.utils import pdf_parser

router = APIRouter(prefix="/jd", tags=["job_descriptions"])


@router.post("/upload", response_model=JDResponse, status_code=status.HTTP_201_CREATED)
def upload_jd(
    request: JDCreateRequest,
    db: Session = Depends(get_db),
    current_recruiter: Recruiter = Depends(get_current_recruiter),
):
    """
    Create a JD from a JSON body containing title and raw_text.
    The JDSummarizerAgent runs automatically to extract skills,
    experience, education, and responsibilities.
    """
    return jd_service.create_jd(
        db=db,
        request=request,
        recruiter_id=current_recruiter.recruiter_id,
    )


@router.post("/upload-file", response_model=JDResponse, status_code=status.HTTP_201_CREATED)
def upload_jd_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_recruiter: Recruiter = Depends(get_current_recruiter),
):
    """
    Create a JD by uploading a PDF file.
    Text is extracted from the PDF via pdfplumber, then passed to
    the JDSummarizerAgent. The filename is used as the JD title.
    """
    raw_bytes = file.file.read()
    if not raw_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )
    raw_text = pdf_parser.extract_text(raw_bytes)
    if not raw_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract any text from the uploaded PDF.",
        )
    title = (file.filename or "Untitled").removesuffix(".pdf")

    request = JDCreateRequest(title=title, raw_text=raw_text)
    return jd_service.create_jd(
        db=db,
        request=request,
        recruiter_id=current_recruiter.recruiter_id,
    )


@router.get("/", response_model=JDListResponse)
def list_jds(
    db: Session = Depends(get_db),
    current_recruiter: Recruiter = Depends(get_current_recruiter),
):
    """
    List all JDs belonging to the authenticated recruiter.
    """
    return jd_service.list_jds(db=db, recruiter_id=current_recruiter.recruiter_id)


@router.get("/{jd_id}", response_model=JDResponse)
def get_jd(
    jd_id: UUID,
    db: Session = Depends(get_db),
    current_recruiter: Recruiter = Depends(get_current_recruiter),
):
    """
    Fetch a single JD by ID.
    Returns 404 if the JD does not exist or belongs to a different recruiter.
    """
    return jd_service.get_jd(
        db=db,
        jd_id=jd_id,
        recruiter_id=current_recruiter.recruiter_id,
    )
