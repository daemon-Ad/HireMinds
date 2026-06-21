import json
import logging
from dataclasses import dataclass, field
from typing import List, Optional

from app.agents.prompts import JD_SUMMARIZER_SYSTEM, JD_SUMMARIZER_USER

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


@dataclass
class ParsedJD:
    required_skills: List[str] = field(default_factory=list)
    min_experience_years: int = 0
    required_education: str = "None"
    responsibilities: List[str] = field(default_factory=list)


class JDSummarizerAgent:
    """
    Takes raw JD text, calls the LLM with the extraction prompt from prompts.py,
    parses the JSON response, retries on malformed output (up to MAX_RETRIES times),
    and returns a ParsedJD dataclass.
    """

    def run(self, title: str, raw_text: str) -> ParsedJD:
        prompt = JD_SUMMARIZER_USER.format(title=title, raw_text=raw_text)

        for attempt in range(1, MAX_RETRIES + 1):
            raw_response = self._call_llm(system=JD_SUMMARIZER_SYSTEM, user=prompt)
            try:
                from app.utils.json_validator import parse_llm_response
                data = parse_llm_response(raw_response)
                if data is None:
                    raise ValueError("parse_llm_response returned None")
                return ParsedJD(
                    required_skills=data.get("required_skills", []),
                    min_experience_years=int(data.get("min_experience_years", 0)),
                    required_education=data.get("required_education", "None"),
                    responsibilities=data.get("responsibilities", []),
                )
            except (json.JSONDecodeError, ValueError, TypeError) as exc:
                logger.warning(
                    "JDSummarizerAgent: attempt %d/%d failed to parse JSON — %s",
                    attempt,
                    MAX_RETRIES,
                    exc,
                )

        logger.error("JDSummarizerAgent: all %d attempts exhausted, returning empty ParsedJD.", MAX_RETRIES)
        return ParsedJD()

    def _call_llm(self, system: str, user: str) -> str:
        """
        Send a prompt to the configured LLM and return the raw response string.
        Replace this method body with your actual LLM client call.
        """
        raise NotImplementedError(
            "JDSummarizerAgent._call_llm is not implemented. "
            "Wire up your LLM client (OpenAI, Gemini, etc.) here."
        )
