import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from app.agents.prompts import MATCHING_KEYWORD_SYSTEM, MATCHING_KEYWORD_USER
from app.agents.jd_summarizer import ParsedJD
from app.agents.cv_parser import ParsedCandidate
from app.config import settings

logger = logging.getLogger(__name__)

# ── Scoring weights (must sum to 1.0) ─────────────────────────────────────────
WEIGHT_SKILL = 0.40
WEIGHT_EXPERIENCE = 0.30
WEIGHT_EDUCATION = 0.20
WEIGHT_KEYWORD = 0.10

# Education level ranking used for experience_score computation
EDUCATION_RANK = {
    "none": 0,
    "high school": 1,
    "associate": 2,
    "bachelor's": 3,
    "bachelor": 3,
    "master's": 4,
    "master": 4,
    "phd": 5,
    "doctorate": 5,
}

MAX_RETRIES = 3


@dataclass
class MatchResult:
    skill_score: float
    experience_score: float
    education_score: float
    keyword_score: float
    overall_score: float
    is_shortlisted: bool


class MatchingEngineAgent:
    """
    Takes a ParsedCandidate and ParsedJD, runs the four-factor weighted scoring
    algorithm. skill_score, experience_score, and education_score are pure Python
    math. Only keyword_score calls the LLM. Returns a MatchResult dataclass.
    """

    def run(self, candidate: ParsedCandidate, jd: ParsedJD) -> MatchResult:
        skill_score = self._score_skills(candidate.skills, jd.required_skills)
        experience_score = self._score_experience(
            candidate.experience_json, jd.min_experience_years
        )
        education_score = self._score_education(
            candidate.education_json, jd.required_education
        )
        keyword_score = self._score_keywords(candidate, jd)

        overall_score = round(
            WEIGHT_SKILL * skill_score
            + WEIGHT_EXPERIENCE * experience_score
            + WEIGHT_EDUCATION * education_score
            + WEIGHT_KEYWORD * keyword_score,
            4,
        )

        return MatchResult(
            skill_score=round(skill_score, 4),
            experience_score=round(experience_score, 4),
            education_score=round(education_score, 4),
            keyword_score=round(keyword_score, 4),
            overall_score=overall_score,
            is_shortlisted=overall_score >= settings.MATCH_THRESHOLD,
        )

    # ── Pure-Python scoring factors ────────────────────────────────────────────

    def _score_skills(
        self, candidate_skills: List[str], required_skills: List[str]
    ) -> float:
        """Jaccard overlap between normalised candidate skills and JD required skills."""
        if not required_skills:
            return 1.0
        req = {s.strip().lower() for s in required_skills}
        cand = {s.strip().lower() for s in candidate_skills}
        matched = req & cand
        return len(matched) / len(req)

    def _score_experience(
        self, experience_json: List[dict], min_experience_years: int
    ) -> float:
        """
        Estimate total years from experience_json list and compare to minimum.
        Each entry may have start_date / end_date strings (YYYY or YYYY-MM).
        Falls back to counting entries × 1.5 years if dates are unparseable.
        """
        if min_experience_years <= 0:
            return 1.0

        total_years = self._estimate_total_years(experience_json)
        ratio = total_years / min_experience_years
        return min(ratio, 1.0)

    def _estimate_total_years(self, experience_json: List[dict]) -> float:
        total = 0.0
        for entry in experience_json:
            start = str(entry.get("start_date", "")).strip()
            end = str(entry.get("end_date", "")).strip().lower()
            try:
                start_year = int(start[:4])
                end_year = datetime.now().year if end in ("present", "current", "") else int(end[:4])
                total += max(0, end_year - start_year)
            except (ValueError, TypeError):
                total += 1.5  # conservative fallback per entry
        return total

    def _score_education(
        self, education_json: List[dict], required_education: str
    ) -> float:
        """
        Compare the highest candidate education level to the JD requirement
        using the EDUCATION_RANK mapping. Returns 1.0 if requirement is met.
        """
        req_key = required_education.strip().lower()
        req_rank = EDUCATION_RANK.get(req_key, 0)
        if req_rank == 0:
            return 1.0  # No specific requirement

        candidate_rank = 0
        for entry in education_json:
            degree = str(entry.get("degree", "")).strip().lower()
            for key, rank in EDUCATION_RANK.items():
                if key in degree:
                    candidate_rank = max(candidate_rank, rank)

        if candidate_rank >= req_rank:
            return 1.0
        elif candidate_rank == req_rank - 1:
            return 0.6
        else:
            return 0.2

    # ── LLM-based keyword scoring ──────────────────────────────────────────────

    def _score_keywords(self, candidate: ParsedCandidate, jd: ParsedJD) -> float:
        candidate_profile = {
            "name": candidate.name,
            "skills": candidate.skills,
            "experience": candidate.experience_json,
            "education": candidate.education_json,
        }
        jd_profile = {
            "required_skills": jd.required_skills,
            "min_experience_years": jd.min_experience_years,
            "required_education": jd.required_education,
            "responsibilities": jd.responsibilities,
        }

        prompt = MATCHING_KEYWORD_USER.format(
            candidate_profile=json.dumps(candidate_profile, indent=2),
            jd_profile=json.dumps(jd_profile, indent=2),
        )

        for attempt in range(1, MAX_RETRIES + 1):
            raw_response = self._call_llm(
                system=MATCHING_KEYWORD_SYSTEM, user=prompt
            )
            try:
                from app.utils.json_validator import parse_llm_response
                data = parse_llm_response(raw_response)
                if data is None:
                    raise ValueError("parse_llm_response returned None")
                score = float(data.get("keyword_score", 0.0))
                return max(0.0, min(1.0, score))
            except (json.JSONDecodeError, ValueError, TypeError) as exc:
                logger.warning(
                    "MatchingEngineAgent: keyword scoring attempt %d/%d failed — %s",
                    attempt,
                    MAX_RETRIES,
                    exc,
                )

        logger.error("MatchingEngineAgent: keyword scoring exhausted retries, defaulting to 0.0.")
        return 0.0

    def _call_llm(self, system: str, user: str) -> str:
        """
        Send a prompt to the configured LLM and return the raw response string.
        Replace this method body with your actual LLM client call.
        """
        raise NotImplementedError(
            "MatchingEngineAgent._call_llm is not implemented. "
            "Wire up your LLM client (OpenAI, Gemini, etc.) here."
        )
