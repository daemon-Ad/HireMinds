from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.config import settings
from app.models.base import Base
from app.models.recruiter import Recruiter
from app.models.job_description import JobDescription
from app.models.candidate import Candidate
from app.models.match import CandidateJDMatch
from app.models.interview import Interview
# ── Engine ─────────────────────────────────────────────────────────────────────
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

# ── Session Factory ────────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# ── Dependency ─────────────────────────────────────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a synchronous database session per request
    and ensures it is closed after the response is sent.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ── Table Creation ─────────────────────────────────────────────────────────────
def create_all_tables() -> None:
    """
    Create all tables defined in ORM metadata.
    Called on startup from main.py lifespan.
    Use Alembic migrations in production.
    """
    Base.metadata.create_all(bind=engine)
