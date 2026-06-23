import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List

from app.agents.jd_summarizer import ParsedJD
from app.agents.cv_parser import ParsedCandidate
from app.config import settings

logger = logging.getLogger(__name__)

# ── Scoring weights (must sum to 1.0) ─────────────────────────────────────────
WEIGHT_SKILL      = 0.40
WEIGHT_EXPERIENCE = 0.30
WEIGHT_EDUCATION  = 0.20
WEIGHT_KEYWORD    = 0.10

# ── Education level hierarchy ──────────────────────────────────────────────────
EDUCATION_RANK = {
    "none": 0,
    "high school": 1,
    "diploma": 2,
    "associate": 2,
    "bachelor's": 3, "bachelor": 3,
    "master's": 4,  "master": 4, "mba": 4,
    "phd": 5, "doctorate": 5,
}

MAX_RETRIES = 3


@dataclass
class MatchResult:
    skill_score:      float
    experience_score: float
    education_score:  float
    keyword_score:    float
    overall_score:    float
    is_shortlisted:   bool


class MatchingEngineAgent:
    """
    Four-factor weighted scoring engine. Fully local — no LLM calls.

    Weights:
        Skills     40%  — set intersection of normalised skill lists
        Experience 30%  — total years vs JD minimum
        Education  20%  — degree hierarchy lookup
        Keywords   10%  — TF-IDF cosine similarity (sklearn)
    """

    def run(self, candidate: ParsedCandidate, jd: ParsedJD) -> MatchResult:
        skill_score      = self._score_skills(candidate.skills, jd.required_skills)
        experience_score = self._score_experience(candidate.experience_json, jd.min_experience_years)
        education_score  = self._score_education(candidate.education_json, jd.required_education)
        keyword_score    = self._score_keywords(candidate, jd)

        overall_score = round(
            WEIGHT_SKILL      * skill_score
            + WEIGHT_EXPERIENCE * experience_score
            + WEIGHT_EDUCATION  * education_score
            + WEIGHT_KEYWORD    * keyword_score,
            4,
        )

        return MatchResult(
            skill_score      = round(skill_score,      4),
            experience_score = round(experience_score, 4),
            education_score  = round(education_score,  4),
            keyword_score    = round(keyword_score,    4),
            overall_score    = overall_score,
            is_shortlisted   = overall_score >= settings.MATCH_THRESHOLD,
        )

    # ── Factor 1: Skills (40%) ─────────────────────────────────────────────────

    def _score_skills(
        self, candidate_skills: List[str], required_skills: List[str]
    ) -> float:
        if not required_skills:
            return 1.0  # No requirement → full score
        
        req = [s.strip().lower() for s in required_skills if s.strip()]
        cand = [s.strip().lower() for s in candidate_skills if s.strip()]
        
        if not req:
            return 1.0
            
        matched_count = 0
        for r in req:
            # Check if required skill is a substring of candidate skill or vice versa
            if any(r in c or c in r for c in cand):
                matched_count += 1
                
        return min(matched_count / len(req), 1.0)

    # ── Factor 2: Experience (30%) ─────────────────────────────────────────────

    def _score_experience(
        self, experience_json: List[dict], min_experience_years: int
    ) -> float:
        if min_experience_years <= 0:
            return 1.0
        total_years = self._estimate_total_years(experience_json)
        return min(total_years / min_experience_years, 1.0)

    def _estimate_total_years(self, experience_json: List[dict]) -> float:
        total = 0.0
        for entry in experience_json:
            start = str(entry.get("start_date", "")).strip()
            end   = str(entry.get("end_date",   "")).strip().lower()
            try:
                start_year = int(start[:4])
                end_year   = (
                    datetime.now().year
                    if end in ("present", "current", "")
                    else int(end[:4])
                )
                total += max(0, end_year - start_year)
            except (ValueError, TypeError):
                total += 1.5  # conservative fallback per unreadable entry
        return total

    # ── Factor 3: Education (20%) ──────────────────────────────────────────────

    def _score_education(
        self, education_json: List[dict], required_education: str
    ) -> float:
        req_key  = required_education.strip().lower()
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

    # ── Factor 4: Keywords (10%) — TF-IDF cosine similarity ───────────────────

    def _score_keywords(
        self, candidate: ParsedCandidate, jd: ParsedJD
    ) -> float:
        # Build candidate text from skills + experience descriptions + roles
        candidate_parts = list(candidate.skills)
        for entry in candidate.experience_json:
            if entry.get("description"):
                candidate_parts.append(entry["description"])
            if entry.get("role"):
                candidate_parts.append(entry["role"])
        candidate_text = " ".join(candidate_parts).strip()

        # Build JD text from required skills + responsibilities
        jd_parts = list(jd.required_skills) + list(jd.responsibilities)
        jd_text  = " ".join(jd_parts).strip()

        if not candidate_text or not jd_text:
            return 0.0

        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                min_df=1,
            )
            matrix = vectorizer.fit_transform([candidate_text, jd_text])
            score  = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
            # TF-IDF cosine similarity tends to be low for short resumes/JDs.
            # Boost the score slightly to make it more representative of a match.
            boosted_score = score * 1.5
            return float(max(0.0, min(1.0, boosted_score)))
        except Exception as exc:
            logger.warning("MatchingEngineAgent: keyword scoring failed — %s", exc)
            return 0.0
