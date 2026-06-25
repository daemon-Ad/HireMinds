from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class JDCreateRequest(BaseModel):
    title: str
    raw_text: str


class JDUpdateRequest(BaseModel):
    title: Optional[str] = None


class JDResponse(BaseModel):
    jd_id: UUID
    recruiter_id: UUID
    title: str
    raw_text: str
    required_skills: Optional[str] = None       # JSON string of extracted skills
    min_experience_years: Optional[int] = None
    required_education: Optional[str] = None
    responsibilities: Optional[str] = None      # JSON string
    created_at: datetime

    model_config = {"from_attributes": True}


class JDListResponse(BaseModel):
    job_descriptions: List[JDResponse]
    total: int
