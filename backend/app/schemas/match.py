from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class MatchResponse(BaseModel):
    match_id: UUID
    candidate_id: UUID
    jd_id: UUID
    recruiter_id: UUID
    skill_score: Optional[float] = None
    experience_score: Optional[float] = None
    education_score: Optional[float] = None
    keyword_score: Optional[float] = None
    overall_score: Optional[float] = None
    is_shortlisted: bool
    matched_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ShortlistResponse(BaseModel):
    jd_id: UUID
    threshold: float
    matches: List[MatchResponse]
    total: int
