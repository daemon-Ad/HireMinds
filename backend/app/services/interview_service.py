import json
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone

from app.schemas.interview import InterviewResponse
from app.db.repositories import match_repo, interview_repo, jd_repo
from app.agents.interview_scheduler import InterviewSchedulerAgent


def send_interviews(
    db: Session,
    jd_id: UUID,
    proposed_slots: List[str],
    recruiter_id: UUID,
) -> List[InterviewResponse]:
    """
    Generate and persist personalised interview invitation emails for all
    shortlisted candidates on a given JD.

    - Validates JD ownership before proceeding.
    - Calls InterviewSchedulerAgent (Groq LLM) once per shortlisted candidate.
    - Uses create_or_update so re-triggering overwrites previous emails.
    - Passes the recruiter's username as the sender name in the email.
    """
    # Ownership check — 404 whether JD missing or belongs to another recruiter
    jd = jd_repo.get_by_id(db=db, jd_id=jd_id)
    if not jd or jd.recruiter_id != recruiter_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description {jd_id} not found.",
        )

    shortlisted = match_repo.get_shortlisted_by_jd_id(db=db, jd_id=jd_id)
    if not shortlisted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No shortlisted candidates found for job description {jd_id}.",
        )

    scheduler = InterviewSchedulerAgent()
    interviews = []

    for match in shortlisted:
        candidate = match.candidate

        result = scheduler.run(
            candidate_name=candidate.name,
            jd_title=jd.title,
            recruiter_name=match.recruiter.username,   # actual recruiter name, not hardcoded
            proposed_slots=proposed_slots,
        )

        interview = interview_repo.create_or_update(
            db=db,
            match_id=match.match_id,
            recruiter_id=recruiter_id,
            email_subject=result.email_subject,
            email_body=result.email_body,
            proposed_slots=json.dumps(result.proposed_slots),
            status="sent",
            sent_at=datetime.now(timezone.utc),
        )
        interviews.append(interview)

    return [InterviewResponse.model_validate(i) for i in interviews]


def list_interviews(db: Session, recruiter_id: UUID) -> List[InterviewResponse]:
    """Return all interviews sent by this recruiter, newest first."""
    interviews = interview_repo.get_by_recruiter_id(db=db, recruiter_id=recruiter_id)
    return [InterviewResponse.model_validate(i) for i in interviews]
