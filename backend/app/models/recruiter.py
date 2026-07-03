import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class Recruiter(Base, TimestampMixin):
    __tablename__ = "recruiters"

    recruiter_id  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username      = Column(String(255), unique=True, nullable=False, index=True)
    email         = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    # The "From:" address used in interview invitation emails.
    # Defaults to the recruiter's account email if not set.
    sender_email  = Column(String(255), nullable=True)

    # Relationships
    job_descriptions = relationship("JobDescription", back_populates="recruiter")
    matches          = relationship("CandidateJDMatch", back_populates="recruiter")


