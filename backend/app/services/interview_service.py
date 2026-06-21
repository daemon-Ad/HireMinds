import json
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone

from app.schemas.interview import InterviewTriggerRequest, InterviewResponse
from app.db.repositories import match_repo, interview_repo, jd_repo
from app.agents.interview_scheduler import InterviewSchedulerAgent


def send_interview(db: Session, request: InterviewTriggerRequest) -> List[InterviewResponse]:
    shortlisted = match_repo.get_shortlisted_by_jd_id(db=db, jd_id=request.jd_id)
    if not shortlisted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No shortlisted candidates found for JD {request.jd_id}.",
        )

    jd = jd_repo.get_by_id(db=db, jd_id=request.jd_id)
    scheduler = InterviewSchedulerAgent()
    interviews = []

    for match in shortlisted:
        candidate = match.candidate

        result = scheduler.run(
            candidate_name=candidate.name,
            jd_title=jd.title if jd else "the role",
            recruiter_name="Recruiter",
            proposed_slots=[],
        )

        interview = interview_repo.create_or_update(
            db=db,
            match_id=match.match_id,
            recruiter_id=match.recruiter_id,
            email_subject=result.email_subject,
            email_body=result.email_body,
            proposed_slots=json.dumps(result.proposed_slots),
            status="sent",
            sent_at=datetime.now(timezone.utc),
        )
        interviews.append(interview)

    return [InterviewResponse.model_validate(i) for i in interviews]


def list_interviews(db: Session) -> List[InterviewResponse]:
    interviews = interview_repo.get_all(db=db)
    return [InterviewResponse.model_validate(i) for i in interviews]
