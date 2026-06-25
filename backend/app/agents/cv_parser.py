from dataclasses import dataclass, field
import logging
from typing import List, Optional

from app.agents.prompts import CV_PARSER_SYSTEM, CV_PARSER_USER
from app.utils.json_validator import parse_llm_response

logger = logging.getLogger(__name__)

MAX_RETRIES = 3

@dataclass
class ParsedCandidate:
    name: str = "Unknown"
    email: str = ""
    phone: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    experience_json: List[dict] = field(default_factory=list)
    education_json: List[dict] = field(default_factory=list)


class CVParserAgent:
    def run(self, raw_cv_text: str) -> ParsedCandidate:
        prompt = CV_PARSER_USER.format(raw_cv_text=raw_cv_text)

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                raw_response = self._call_llm(
                    system=CV_PARSER_SYSTEM,
                    user=prompt,
                )
            except Exception as exc:
                logger.warning(
                    "CVParserAgent: LLM call attempt %d/%d failed — %s",
                    attempt, MAX_RETRIES, exc,
                )
                continue

            data = parse_llm_response(raw_response)
            if data is None:
                logger.warning(
                    "CVParserAgent: attempt %d/%d — parse_llm_response returned None",
                    attempt, MAX_RETRIES,
                )
                continue

            parsed = self._build_parsed_candidate(data)
            logger.info(
                "CVParserAgent: extracted candidate %s, email: %s, %d skills",
                parsed.name, parsed.email, len(parsed.skills)
            )
            return parsed

        logger.error(
            "CVParserAgent: all %d LLM attempts failed, returning empty ParsedCandidate.",
            MAX_RETRIES,
        )
        return ParsedCandidate()

    def _call_llm(self, system: str, user: str) -> str:
        from groq import Groq
        from app.config import settings

        client = Groq(api_key=settings.GROQ_API_KEY)
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            temperature=0.0,
            max_tokens=1500,
        )
        return response.choices[0].message.content

    def _build_parsed_candidate(self, data: dict) -> ParsedCandidate:
        name = str(data.get("name", "Unknown")).strip()
        email = str(data.get("email", "")).strip()
        phone = data.get("phone")
        if phone is not None:
            phone = str(phone).strip()

        raw_skills = data.get("skills", [])
        if isinstance(raw_skills, list):
            skills = [str(s).strip() for s in raw_skills if s]
        else:
            skills = []

        raw_exp = data.get("experience_json", [])
        experience_json = []
        if isinstance(raw_exp, list):
            for exp in raw_exp:
                if isinstance(exp, dict):
                    experience_json.append(exp)

        raw_edu = data.get("education_json", [])
        education_json = []
        if isinstance(raw_edu, list):
            for edu in raw_edu:
                if isinstance(edu, dict):
                    education_json.append(edu)

        return ParsedCandidate(
            name=name,
            email=email,
            phone=phone,
            skills=skills,
            experience_json=experience_json,
            education_json=education_json
        )
