from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import create_all_tables
from app.routers import auth, job_descriptions, candidates, matches, interviews


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all_tables()
    yield


app = FastAPI(
    title="Multi-Agent AI Recruitment Platform",
    description="AI-powered recruitment pipeline: JD parsing, CV matching, and interview scheduling.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS (React frontend) ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(job_descriptions.router)
app.include_router(candidates.router)
app.include_router(matches.router)
app.include_router(interviews.router)
