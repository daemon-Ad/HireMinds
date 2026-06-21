import json
import logging
from dataclasses import dataclass, field
from typing import List, Optional

from app.agents.prompts import CV_PARSER_SYSTEM, CV_PARSER_USER

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
    """
    Takes raw CV text, calls the LLM with the extraction prompt from prompts.py,
    parses the JSON response, retries on malformed output (up to MAX_RETRIES times),
    and returns a ParsedCandidate dataclass with structured skills, experience list,
    and education.
    """

    def run(self, raw_cv_text: str) -> ParsedCandidate:
        prompt = CV_PARSER_USER.format(raw_cv_text=raw_cv_text)

        for attempt in range(1, MAX_RETRIES + 1):
            raw_response = self._call_llm(system=CV_PARSER_SYSTEM, user=prompt)
            try:
                from app.utils.json_validator import parse_llm_response
                data = parse_llm_response(raw_response)
                if data is None:
                    raise ValueError("parse_llm_response returned None")
                return ParsedCandidate(
                    name=data.get("name", "Unknown"),
                    email=data.get("email", ""),
                    phone=data.get("phone"),
                    skills=data.get("skills", []),
                    experience_json=data.get("experience_json", []),
                    education_json=data.get("education_json", []),
                )
            except (json.JSONDecodeError, ValueError, TypeError) as exc:
                logger.warning(
                    "CVParserAgent: attempt %d/%d failed to parse JSON — %s",
                    attempt,
                    MAX_RETRIES,
                    exc,
                )

        logger.error("CVParserAgent: all %d attempts exhausted, returning empty ParsedCandidate.", MAX_RETRIES)
        return ParsedCandidate()

    def _call_llm(self, system: str, user: str) -> str:
        """
        Send a prompt to the configured LLM and return the raw response string.
        Replace this method body with your actual LLM client call.
        """
        raise NotImplementedError(
            "CVParserAgent._call_llm is not implemented. "
            "Wire up your LLM client (OpenAI, Gemini, etc.) here."
        )
