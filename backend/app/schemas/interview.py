from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class InterviewTriggerRequest(BaseModel):
    jd_id: UUID
    candidate_id: Optional[UUID] = None
    proposed_slots: List[str] = []     # e.g. ["2026-07-01 10:00 AM", "2026-07-02 2:00 PM"]

class InterviewUpdateRequest(BaseModel):
    action: str  # "cancel" or "postpone"
    new_slots: List[str] = []

class InterviewResponse(BaseModel):
    interview_id: UUID
    match_id: UUID
    recruiter_id: UUID
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    proposed_slots: Optional[str] = None   # JSON string
    status: str                             # pending / sent / failed
    sent_at: Optional[datetime] = None
    candidate_name: Optional[str] = None
    jd_title: Optional[str] = None

    model_config = {"from_attributes": True}
