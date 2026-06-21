import uuid
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class JobDescription(Base, TimestampMixin):
    __tablename__ = "job_descriptions"

    jd_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    recruiter_id = Column(
        UUID(as_uuid=True),
        ForeignKey("recruiters.recruiter_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(255), nullable=False)
    raw_text = Column(Text, nullable=False)
    required_skills = Column(Text, nullable=True)       # JSON string
    min_experience_years = Column(Integer, nullable=True)
    required_education = Column(String(255), nullable=True)
    responsibilities = Column(Text, nullable=True)      # JSON string

    # Relationships
    recruiter = relationship("Recruiter", back_populates="job_descriptions")
    matches = relationship("CandidateJDMatch", back_populates="job_description")
