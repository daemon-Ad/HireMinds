import logging
from uuid import UUID
from sqlalchemy.orm import Session

from app.db.repositories import jd_repo
from app.services import matching_service

logger = logging.getLogger(__name__)


def run_matching_pipeline(db: Session, candidate_id: UUID, recruiter_id: UUID) -> None:
    """
    Pipeline coordinator called by candidate_service after a CV is parsed.
    Loops through all JDs belonging to the uploading recruiter and calls
    matching_service for each (candidate, JD) pair, producing a
    CandidateJDMatch record per pair.

    Scoped to recruiter_id so a CV upload only triggers matching against
    that recruiter's own job descriptions — not system-wide.
    """
    recruiter_jds = jd_repo.get_by_recruiter(db=db, recruiter_id=recruiter_id)

    if not recruiter_jds:
        logger.info(
            "Matching pipeline: recruiter=%s has no JDs yet — skipping matching for candidate=%s",
            recruiter_id, candidate_id,
        )
        return

    for jd in recruiter_jds:
        try:
            matching_service.run_match(
                db=db,
                candidate_id=candidate_id,
                jd_id=jd.jd_id,
            )
        except Exception as exc:
            logger.warning(
                "Matching pipeline: failed for candidate=%s jd=%s — %s",
                candidate_id, jd.jd_id, exc,
            )
            continue
