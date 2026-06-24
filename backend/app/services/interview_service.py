import json
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone, timedelta

from app.schemas.interview import InterviewResponse
from app.db.repositories import match_repo, interview_repo, jd_repo
from app.agents.interview_scheduler import InterviewSchedulerAgent

def parse_datetime(dt_str: str) -> datetime:
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except ValueError:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M", "%m/%d/%Y %H:%M", "%Y-%m-%d %I:%M %p", "%Y-%m-%d %I:%M%p"):
            try:
                return datetime.strptime(dt_str.strip(), fmt)
            except ValueError:
                continue
        raise ValueError(f"Could not parse datetime string: {dt_str}")

def get_next_free_slot(db: Session, recruiter_id: UUID, start_time: datetime, additional_taken_slots: List[datetime] = None) -> datetime:
    existing_interviews = interview_repo.get_by_recruiter_id(db=db, recruiter_id=recruiter_id)
    taken_slots = []
    if additional_taken_slots:
        taken_slots.extend(additional_taken_slots)

    for iv in existing_interviews:
        if iv.status not in ["cancelled", "failed", "rejected", "postponed"]:
            if iv.proposed_slots:
                try:
                    slots = json.loads(iv.proposed_slots)
                    for s in slots:
                        try:
                            dt = parse_datetime(s)
                            if dt.tzinfo is None:
                                dt = dt.replace(tzinfo=timezone.utc)
                            taken_slots.append(dt)
                        except Exception:
                            pass
                except Exception:
                    pass

    taken_slots.sort()

    while True:
        if start_time.hour > 17 or (start_time.hour == 17 and start_time.minute > 30):
            start_time += timedelta(days=1)
            start_time = start_time.replace(hour=9, minute=30, second=0, microsecond=0)
        elif start_time.hour < 9 or (start_time.hour == 9 and start_time.minute < 30):
            start_time = start_time.replace(hour=9, minute=30, second=0, microsecond=0)

        collision = False
        for ts in taken_slots:
            diff = abs((start_time - ts).total_seconds())
            if diff < 40 * 60:
                collision = True
                start_time = ts + timedelta(minutes=40)
                break
        
        if not collision:
            break
            
    return start_time


def send_interviews(
    db: Session,
    jd_id: UUID,
    proposed_slots: List[str],
    recruiter_id: UUID,
    candidate_id: Optional[UUID] = None,
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

    target_matches = []
    if candidate_id:
        single_match = match_repo.get_by_jd_and_candidate(db=db, jd_id=jd_id, candidate_id=candidate_id)
        if not single_match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Match record not found for candidate {candidate_id}.",
            )
        target_matches = [single_match]
    else:
        target_matches = match_repo.get_shortlisted_by_jd_id(db=db, jd_id=jd_id)
        if not target_matches:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No shortlisted candidates found for job description {jd_id}.",
            )

    scheduler = InterviewSchedulerAgent()
    interviews = []
    batch_taken_slots = []

    for match in target_matches:
        candidate = match.candidate

        candidate_adjusted_slots = []
        for slot_str in proposed_slots:
            try:
                dt = parse_datetime(slot_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                
                free_dt = get_next_free_slot(db, recruiter_id, dt, batch_taken_slots)
                batch_taken_slots.append(free_dt)
                candidate_adjusted_slots.append(free_dt.strftime("%Y-%m-%d %I:%M %p"))
            except ValueError:
                candidate_adjusted_slots.append(slot_str)

        result = scheduler.run(
            candidate_name=candidate.name,
            jd_title=jd.title,
            recruiter_name=match.recruiter.username,   # actual recruiter name, not hardcoded
            proposed_slots=candidate_adjusted_slots,
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

def update_interview(
    db: Session,
    interview_id: UUID,
    recruiter_id: UUID,
    action: str,
    new_slots: List[str]
) -> InterviewResponse:
    interview = interview_repo.get_by_id(db=db, interview_id=interview_id)
    if not interview or interview.recruiter_id != recruiter_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview {interview_id} not found."
        )

    match = interview.match
    candidate = match.candidate
    jd = match.job_description

    adjusted_new_slots = []
    for slot_str in new_slots:
        try:
            dt = parse_datetime(slot_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            
            free_dt = get_next_free_slot(db, recruiter_id, dt)
            adjusted_new_slots.append(free_dt.strftime("%Y-%m-%d %I:%M %p"))
        except ValueError:
            adjusted_new_slots.append(slot_str)

    scheduler = InterviewSchedulerAgent()
    result = scheduler.update_interview(
        candidate_name=candidate.name,
        jd_title=jd.title,
        recruiter_name=match.recruiter.username,
        action=action,
        proposed_slots=adjusted_new_slots
    )

    if action == "cancel":
        new_status = "cancelled"
    else:
        if interview.status.value == "postponed":
            new_status = "sent"
        else:
            new_status = "postponed"

    interview = interview_repo.create_or_update(
        db=db,
        match_id=match.match_id,
        recruiter_id=recruiter_id,
        email_subject=result.email_subject,
        email_body=result.email_body,
        proposed_slots=json.dumps(result.proposed_slots),
        status=new_status,
        sent_at=datetime.now(timezone.utc),
    )

    return InterviewResponse.model_validate(interview)
