import uuid
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class Candidate(Base, TimestampMixin):
    __tablename__ = "candidates"

    candidate_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    skills = Column(Text, nullable=True)            # JSON string
    experience_json = Column(Text, nullable=True)   # JSON string
    education_json = Column(Text, nullable=True)    # JSON string
    raw_cv_text = Column(Text, nullable=True)

    # Relationships
    matches = relationship("CandidateJDMatch", back_populates="candidate")
