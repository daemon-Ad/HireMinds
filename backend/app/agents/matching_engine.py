import logging
from dataclasses import dataclass
from typing import List
import json

from app.agents.jd_summarizer import ParsedJD
from app.agents.cv_parser import ParsedCandidate
from app.agents.prompts import MATCHING_ENGINE_SYSTEM, MATCHING_ENGINE_USER
from app.utils.json_validator import parse_llm_response
from app.config import settings

logger = logging.getLogger(__name__)

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
    Evaluates candidate alignment using Groq LLaMA model based on priorities:
    Skills (40%), Experience (30%), Education (20%), Keywords (10%).
    """

    def run(self, candidate: ParsedCandidate, jd: ParsedJD) -> MatchResult:
        candidate_profile = json.dumps({
            "name": candidate.name,
            "skills": candidate.skills,
            "experience": candidate.experience_json,
            "education": candidate.education_json,
        }, indent=2)

        jd_profile = json.dumps({
            "required_skills": jd.required_skills,
            "min_experience_years": jd.min_experience_years,
            "required_education": jd.required_education,
            "responsibilities": jd.responsibilities,
        }, indent=2)

        prompt = MATCHING_ENGINE_USER.format(
            candidate_profile=candidate_profile,
            jd_profile=jd_profile
        )

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                raw_response = self._call_llm(
                    system=MATCHING_ENGINE_SYSTEM,
                    user=prompt,
                )
            except Exception as exc:
                logger.warning(
                    "MatchingEngineAgent: LLM call attempt %d/%d failed — %s",
                    attempt, MAX_RETRIES, exc,
                )
                continue

            data = parse_llm_response(raw_response)
            if data is None:
                logger.warning(
                    "MatchingEngineAgent: attempt %d/%d — parse_llm_response returned None",
                    attempt, MAX_RETRIES,
                )
                continue

            try:
                skill_score = float(data.get("skill_score", 0.0))
                experience_score = float(data.get("experience_score", 0.0))
                education_score = float(data.get("education_score", 0.0))
                keyword_score = float(data.get("keyword_score", 0.0))
                overall_score = float(data.get("overall_score", 0.0))

                return MatchResult(
                    skill_score=skill_score,
                    experience_score=experience_score,
                    education_score=education_score,
                    keyword_score=keyword_score,
                    overall_score=overall_score,
                    is_shortlisted=overall_score >= settings.MATCH_THRESHOLD,
                )
            except (ValueError, TypeError) as exc:
                logger.warning("MatchingEngineAgent: invalid score format — %s", exc)
                continue

        logger.error("MatchingEngineAgent: all LLM attempts failed, returning 0 scores.")
        return MatchResult(0.0, 0.0, 0.0, 0.0, 0.0, False)

    def _call_llm(self, system: str, user: str) -> str:
        from groq import Groq
        
        client = Groq(api_key=settings.GROQ_API_KEY)
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            temperature=0.0,
            max_tokens=1024,
        )
        return response.choices[0].message.content
