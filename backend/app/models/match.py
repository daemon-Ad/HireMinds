import uuid
from sqlalchemy import Column, Float, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class CandidateJDMatch(Base, TimestampMixin):
    __tablename__ = "candidate_jd_matches"

    __table_args__ = (
        UniqueConstraint("candidate_id", "jd_id", name="uq_candidate_jd"),
    )

    match_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    candidate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("candidates.candidate_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    jd_id = Column(
        UUID(as_uuid=True),
        ForeignKey("job_descriptions.jd_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recruiter_id = Column(
        UUID(as_uuid=True),
        ForeignKey("recruiters.recruiter_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_score = Column(Float, nullable=True)
    experience_score = Column(Float, nullable=True)
    education_score = Column(Float, nullable=True)
    keyword_score = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True)
    is_shortlisted = Column(Boolean, default=False, nullable=False)
    matched_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    candidate = relationship("Candidate", back_populates="matches")
    job_description = relationship("JobDescription", back_populates="matches")
    recruiter = relationship("Recruiter", back_populates="matches")
    interview = relationship("Interview", back_populates="match", uselist=False)
