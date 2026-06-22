import re
import logging
from dataclasses import dataclass, field
from typing import List

from app.utils.skills_vocab import match_skills

logger = logging.getLogger(__name__)

# ── Compiled patterns (module-level, not inside functions) ─────────────────────

# Experience: "3+ years of experience", "minimum 2 years", "at least 5 years"
_EXP_PATTERNS = [
    re.compile(r'(\d+)\+?\s*years?\s+of\s+experience', re.IGNORECASE),
    re.compile(r'(\d+)\+?\s*years?\s+experience', re.IGNORECASE),
    re.compile(r'experience\s+of\s+(\d+)\+?\s*years?', re.IGNORECASE),
    re.compile(r'minimum\s+(\d+)\s+years?', re.IGNORECASE),
    re.compile(r'at\s+least\s+(\d+)\s+years?', re.IGNORECASE),
]

# Education: ordered highest to lowest so first match wins
_EDU_PATTERNS = [
    (re.compile(r'\bphd\b|\bdoctorate\b', re.IGNORECASE), "PhD"),
    (re.compile(r"\bmaster[s']?\b|\bm\.sc\b|\bmba\b|\bm\.s\b", re.IGNORECASE), "Master's"),
    (re.compile(r"\bbachelor[s']?\b|\bb\.sc\b|\bb\.tech\b|\bbeng\b|\bb\.s\b|\bb\.e\b", re.IGNORECASE), "Bachelor's"),
    (re.compile(r'\bdiploma\b', re.IGNORECASE), "Diploma"),
    (re.compile(r'\bhigh\s+school\b|\bsecondary\b', re.IGNORECASE), "High School"),
]

# Responsibility section headers
_RESP_HEADER = re.compile(
    r'(?i)(responsibilit|you\s+will|what\s+you.{0,4}ll\s+do|your\s+role|'
    r'duties|key\s+tasks|what\s+we\s+expect|job\s+duties|what\s+you.{0,4}ll\s+be\s+doing)',
)

# Bullet point lines
_BULLET = re.compile(r'(?m)^[\s]*[-•*▪▸]\s*(.+)$')

# Action verbs that indicate a responsibility sentence
_ACTION_VERBS = re.compile(
    r'\b(develop|design|build|manage|lead|coordinate|implement|maintain|create|'
    r'analys|analyz|ensure|oversee|collaborat|support|deliver|conduct|establish|'
    r'monitor|review|assist|prepare|provide|improve|drive|execute|deploy)\b',
    re.IGNORECASE,
)


@dataclass
class ParsedJD:
    required_skills: List[str] = field(default_factory=list)
    min_experience_years: int = 0
    required_education: str = "None"
    responsibilities: List[str] = field(default_factory=list)


class JDSummarizerAgent:
    """
    Extracts structured fields from free-form job description prose.
    Fully local — no LLM calls.
    Designed for the Kaggle 'Job Title and Job Description' dataset
    which has two columns: Job Title and Job Description (raw prose, no
    guaranteed section headers).
    """

    def run(self, title: str, raw_text: str) -> ParsedJD:
        # STEP 1 — Extract skills via vocabulary matching
        required_skills = self._extract_skills(raw_text)

        # STEP 2 — Extract minimum experience years
        min_experience_years = self._extract_experience(raw_text)

        # STEP 3 — Extract required education
        required_education = self._extract_education(raw_text)

        # STEP 4 — Extract responsibilities
        responsibilities = self._extract_responsibilities(raw_text)

        return ParsedJD(
            required_skills=required_skills,
            min_experience_years=min_experience_years,
            required_education=required_education,
            responsibilities=responsibilities,
        )

    # ── Private extraction methods ─────────────────────────────────────────────

    def _extract_skills(self, text: str) -> List[str]:
        """Vocabulary matching against skills_vocabulary.txt."""
        matched = match_skills(text)
        return sorted(set(matched))

    def _extract_experience(self, text: str) -> int:
        """
        Try all experience patterns; collect all numeric matches and
        return the maximum value found. Returns 0 if nothing matched.
        """
        all_values = []
        for pattern in _EXP_PATTERNS:
            for m in pattern.finditer(text):
                try:
                    all_values.append(int(m.group(1)))
                except (ValueError, IndexError):
                    pass
        return max(all_values) if all_values else 0

    def _extract_education(self, text: str) -> str:
        """
        Scan for education keywords in priority order (highest degree first).
        Returns the first match found, or "None" if nothing matched.
        """
        for pattern, label in _EDU_PATTERNS:
            if pattern.search(text):
                return label
        return "None"

    def _extract_responsibilities(self, text: str) -> List[str]:
        """
        Two-strategy extraction:
        1. If a known responsibilities header is found, extract bullet
           points (or sentences) from the text that follows it.
        2. If no header found, scan full text for action-verb sentences.
        Returns up to 5 responsibility strings.
        """
        header_match = _RESP_HEADER.search(text)

        if header_match:
            # Take up to 1200 chars after the header
            after_header = text[header_match.end(): header_match.end() + 1200]

            # Try bullet extraction first
            bullets = _BULLET.findall(after_header)
            if bullets:
                return [b.strip() for b in bullets[:5] if b.strip()]

            # Fall back to sentence splitting within that block
            sentences = re.split(r'(?<=[.!?])\s+', after_header)
            cleaned = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
            return cleaned[:5]

        # No header found — scan full text for action-verb sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        action_sentences = [
            s.strip() for s in sentences
            if s.strip() and _ACTION_VERBS.search(s) and len(s.strip()) > 20
        ]
        return action_sentences[:5]
