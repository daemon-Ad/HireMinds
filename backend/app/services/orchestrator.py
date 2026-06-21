import logging
from uuid import UUID
from sqlalchemy.orm import Session

from app.db.repositories import jd_repo
from app.services import matching_service

logger = logging.getLogger(__name__)


def run_matching_pipeline(db: Session, candidate_id: UUID) -> None:
    """
    Pipeline coordinator called by candidate_service after a CV is parsed.
    Loops through all JDs in the system and calls matching_service for each
    (candidate, JD) pair, producing a CandidateJDMatch record for every pair.
    """
    all_jds = jd_repo.get_all(db=db)

    for jd in all_jds:
        try:
            matching_service.run_match(
                db=db,
                candidate_id=candidate_id,
                jd_id=jd.jd_id,
            )
        except Exception as exc:
            logger.warning(
                "Matching pipeline: failed for candidate=%s jd=%s — %s",
                candidate_id, jd.jd_id, exc
            )
            continue
