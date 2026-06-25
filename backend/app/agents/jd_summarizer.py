import logging
import re
from dataclasses import dataclass, field
from typing import List

from app.agents.prompts import JD_SUMMARIZER_SYSTEM, JD_SUMMARIZER_USER
from app.utils.json_validator import parse_llm_response

logger = logging.getLogger(__name__)

MAX_RETRIES = 3

# ── Valid education values (must match MatchingEngineAgent's EDUCATION_RANK keys) ─
_VALID_EDUCATION = {"PhD", "Master's", "Bachelor's", "Diploma", "High School", "None"}

# ── Fallback regex patterns (used only if LLM fails entirely) ─────────────────
_EXP_PATTERNS = [
    re.compile(r'(\d+)\+?\s*years?\s+of\s+experience', re.IGNORECASE),
    re.compile(r'(\d+)\+?\s*years?\s+experience', re.IGNORECASE),
    re.compile(r'minimum\s+(\d+)\s+years?', re.IGNORECASE),
    re.compile(r'at\s+least\s+(\d+)\s+years?', re.IGNORECASE),
]
_EDU_PATTERNS = [
    (re.compile(r'\bphd\b|\bdoctorate\b', re.IGNORECASE), "PhD"),
    (re.compile(r"\bmaster[s']?\b|\bm\.sc\b|\bmba\b", re.IGNORECASE), "Master's"),
    (re.compile(r"\bbachelor[s']?\b|\bb\.sc\b|\bb\.tech\b|\bb\.e\b", re.IGNORECASE), "Bachelor's"),
    (re.compile(r'\bdiploma\b', re.IGNORECASE), "Diploma"),
    (re.compile(r'\bhigh\s+school\b', re.IGNORECASE), "High School"),
]


@dataclass
class ParsedJD:
    """
    The data contract between JDSummarizerAgent and every downstream consumer.

    Fields
    ------
    required_skills      : list[str]  — normalized skill names (e.g. "JavaScript")
    min_experience_years : int        — minimum years required (0 = unspecified)
    required_education   : str        — one of the keys in MatchingEngineAgent.EDUCATION_RANK
    responsibilities     : list[str]  — up to 6 key responsibility strings

    IMPORTANT: Do not rename or retype these fields.
    They are read by:
      - jd_service.py        (json.dumps each field into the DB)
      - matching_service.py  (_orm_to_parsed_jd rebuilds this dataclass from the DB)
      - matching_engine.py   (MatchingEngineAgent.run consumes this dataclass)
    """
    required_skills:      List[str] = field(default_factory=list)
    min_experience_years: int       = 0
    required_education:   str       = "None"
    responsibilities:     List[str] = field(default_factory=list)


class JDSummarizerAgent:
    """
    Extracts structured fields from free-form job description text via Groq LLaMA.

    Why LLM instead of regex/vocabulary?
    - JDs use varied language, synonyms, and implicit requirements that a fixed
      vocabulary list cannot reliably capture.
    - Runs once per JD upload (low volume), so latency is acceptable.
    - Only this agent and InterviewSchedulerAgent use an LLM; all other agents
      (CV parser, matching engine) remain fully local.

    Fallback: if the LLM is unavailable or returns unparseable output after
    MAX_RETRIES attempts, a regex-based extractor is used so the system never
    crashes on JD upload.
    """

    def run(self, title: str, raw_text: str) -> ParsedJD:
        prompt = JD_SUMMARIZER_USER.format(title=title, raw_text=raw_text)

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                raw_response = self._call_llm(
                    system=JD_SUMMARIZER_SYSTEM,
                    user=prompt,
                )
            except Exception as exc:
                logger.warning(
                    "JDSummarizerAgent: LLM call attempt %d/%d failed — %s",
                    attempt, MAX_RETRIES, exc,
                )
                continue

            data = parse_llm_response(raw_response)
            if data is None:
                logger.warning(
                    "JDSummarizerAgent: attempt %d/%d — parse_llm_response returned None",
                    attempt, MAX_RETRIES,
                )
                continue

            parsed = self._build_parsed_jd(data)
            logger.info(
                "JDSummarizerAgent: extracted %d skills, %d years exp, edu=%s, %d responsibilities",
                len(parsed.required_skills),
                parsed.min_experience_years,
                parsed.required_education,
                len(parsed.responsibilities),
            )
            return parsed

        # All LLM attempts exhausted — fall back to regex so upload never fails
        logger.error(
            "JDSummarizerAgent: all %d LLM attempts failed, using regex fallback.",
            MAX_RETRIES,
        )
        return self._regex_fallback(raw_text)

    # ── Private helpers ────────────────────────────────────────────────────────

    def _call_llm(self, system: str, user: str) -> str:
        """
        Calls Groq's LLaMA model. Instantiated here (not at class init) so the
        import only happens when actually called — keeping unit tests fast and
        the agent importable without GROQ_API_KEY being set.
        """
        from groq import Groq
        from app.config import settings

        client = Groq(api_key=settings.GROQ_API_KEY)
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            temperature=0.0,    # deterministic — we want consistent structured output
            max_tokens=1024,
        )
        return response.choices[0].message.content

    def _build_parsed_jd(self, data: dict) -> ParsedJD:
        """
        Safely converts the raw LLM dict into a ParsedJD, coercing types
        where the model may have returned a slightly wrong format.
        """
        # required_skills: must be list[str]
        raw_skills = data.get("required_skills", [])
        if isinstance(raw_skills, list):
            required_skills = [str(s).strip() for s in raw_skills if s]
        else:
            required_skills = []

        # min_experience_years: must be int; LLM sometimes returns "3" or 3.0
        raw_exp = data.get("min_experience_years", 0)
        try:
            min_experience_years = int(float(str(raw_exp)))
        except (ValueError, TypeError):
            min_experience_years = 0
        min_experience_years = max(0, min_experience_years)  # no negatives

        # required_education: must be one of the valid strings
        raw_edu = str(data.get("required_education", "None")).strip()
        required_education = raw_edu if raw_edu in _VALID_EDUCATION else "None"

        # responsibilities: must be list[str]
        raw_resp = data.get("responsibilities", [])
        if isinstance(raw_resp, list):
            responsibilities = [str(r).strip() for r in raw_resp if r][:6]
        else:
            responsibilities = []

        return ParsedJD(
            required_skills=required_skills,
            min_experience_years=min_experience_years,
            required_education=required_education,
            responsibilities=responsibilities,
        )

    def _regex_fallback(self, raw_text: str) -> ParsedJD:
        """
        Minimal regex-based extractor used only when Groq is completely
        unavailable. Returns a best-effort ParsedJD so the upload endpoint
        never returns a 500 error.
        """
        # Experience
        exp_values = []
        for pattern in _EXP_PATTERNS:
            for m in pattern.finditer(raw_text):
                try:
                    exp_values.append(int(m.group(1)))
                except (ValueError, IndexError):
                    pass
        min_experience_years = max(exp_values) if exp_values else 0

        # Education
        required_education = "None"
        for pattern, label in _EDU_PATTERNS:
            if pattern.search(raw_text):
                required_education = label
                break

        return ParsedJD(
            required_skills=[],
            min_experience_years=min_experience_years,
            required_education=required_education,
            responsibilities=[],
        )
