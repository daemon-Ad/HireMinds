from __future__ import annotations
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class InterviewTriggerRequest(BaseModel):
    jd_id: UUID


class InterviewResponse(BaseModel):
    interview_id: UUID
    match_id: UUID
    recruiter_id: UUID
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    proposed_slots: Optional[str] = None   # JSON string
    status: str                             # pending / sent / failed
    sent_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
