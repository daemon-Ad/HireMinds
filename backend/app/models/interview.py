import uuid
import enum
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class InterviewStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Interview(Base, TimestampMixin):
    __tablename__ = "interviews"

    interview_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    match_id = Column(
        UUID(as_uuid=True),
        ForeignKey("candidate_jd_matches.match_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,    # one interview per match
        index=True,
    )
    recruiter_id = Column(
        UUID(as_uuid=True),
        ForeignKey("recruiters.recruiter_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email_subject = Column(String(500), nullable=True)
    email_body = Column(Text, nullable=True)
    proposed_slots = Column(Text, nullable=True)    # JSON string
    status = Column(
        SAEnum(InterviewStatus),
        default=InterviewStatus.PENDING,
        nullable=False,
    )
    sent_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    match = relationship("CandidateJDMatch", back_populates="interview")
