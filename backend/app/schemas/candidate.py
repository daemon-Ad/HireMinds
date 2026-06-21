from __future__ import annotations
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr


class CandidateResponse(BaseModel):
    candidate_id: UUID
    name: str
    email: EmailStr
    phone: Optional[str] = None
    skills: Optional[str] = None            # JSON string
    experience_json: Optional[str] = None   # JSON string
    education_json: Optional[str] = None    # JSON string
    raw_cv_text: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CandidateWithScoreResponse(BaseModel):
    candidate_id: UUID
    name: str
    email: EmailStr
    phone: Optional[str] = None
    skills: Optional[str] = None
    experience_json: Optional[str] = None
    education_json: Optional[str] = None
    raw_cv_text: Optional[str] = None
    created_at: datetime
    # Match score against a specific JD
    overall_score: Optional[float] = None
    skill_score: Optional[float] = None
    experience_score: Optional[float] = None
    education_score: Optional[float] = None
    keyword_score: Optional[float] = None
    is_shortlisted: bool = False

    model_config = {"from_attributes": True}
