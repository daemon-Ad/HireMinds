from dataclasses import dataclass, field
import re
from typing import List, Optional
import spacy

from app.utils.skills_vocab import match_skills

# Regex patterns compiled at module level as constants
EMAIL_PATTERN = re.compile(r'[\w.+\-]+@[\w\-]+\.[a-zA-Z]{2,}')
PHONE_PATTERN = re.compile(r'(\+?\d[\d\s\-().]{7,}\d)')
EXP_DATE_PATTERN = re.compile(r'\((\d{4})\s*[-–]\s*(\d{4}|present|current)\)', re.IGNORECASE)
EDU_DATE_PATTERN = re.compile(r'(\d{4})\s*[-–]\s*(\d{4}|present)', re.IGNORECASE)
EDU_YEAR_FALLBACK_PATTERN = re.compile(r'\b(19|20)\d{2}\b')
ONLY_DATE_PATTERN = re.compile(r'^[\d\s\-–()|present|current]+$', re.IGNORECASE)


@dataclass
class ParsedCandidate:
    name: str = "Unknown"
    email: str = ""
    phone: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    experience_json: List[dict] = field(default_factory=list)
    education_json: List[dict] = field(default_factory=list)


class CVParserAgent:
    _nlp = spacy.load("en_core_web_sm")

    def run(self, raw_cv_text: str) -> ParsedCandidate:
        # STEP 1 — Split into header block and sections
        SECTION_HEADERS = [
            "education", "work experience", "experience", "employment",
            "skills", "certifications", "achievements", "tech stack",
            "projects", "summary", "objective"
        ]

        lines = [line.strip() for line in raw_cv_text.splitlines()]

        first_header_idx = -1
        for idx, line in enumerate(lines):
            line_lower = line.lower()
            if any(line_lower == h or line_lower.startswith(h) for h in SECTION_HEADERS):
                first_header_idx = idx
                break

        if first_header_idx == -1:
            header_block = "\n".join(lines)
            body_lines = []
        else:
            header_block = "\n".join(lines[:first_header_idx])
            body_lines = lines[first_header_idx:]

        sections = {}
        current_section = None
        current_lines = []
        for line in body_lines:
            line_lower = line.lower()
            if line_lower in SECTION_HEADERS:
                if current_section is not None:
                    sections[current_section] = "\n".join(current_lines).strip()
                current_section = line_lower
                current_lines = []
            else:
                if current_section is not None:
                    current_lines.append(line)
        if current_section is not None:
            sections[current_section] = "\n".join(current_lines).strip()

        # STEP 2 — Extract name, email, phone from HEADER_BLOCK
        email_match = EMAIL_PATTERN.search(header_block)
        email = email_match.group(0) if email_match else ""

        phone_match = PHONE_PATTERN.search(header_block)
        phone = phone_match.group(0).strip() if phone_match else None

        # Patterns that indicate a non-name header line
        _SKIP_LINE_PATTERN = re.compile(
            r'(resume|curriculum\s*vitae|cv\b|candidate|id\s*:|profile)',
            re.IGNORECASE,
        )

        name = "Unknown"
        header_lines = header_block.splitlines()
        for line in header_lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue
            if email and email in stripped_line:
                continue
            if phone and phone in stripped_line:
                continue
            if _SKIP_LINE_PATTERN.search(stripped_line):
                continue
            # Handle "Name: Thomas Baird" format
            name_prefix = re.match(r'(?i)^name\s*:\s*(.+)', stripped_line)
            if name_prefix:
                name = name_prefix.group(1).strip()
            else:
                name = stripped_line
            break

        # STEP 3 — Extract skills
        skills_list = []
        tech_stack_text = sections.get("tech stack", "")
        if tech_stack_text:
            for token in tech_stack_text.split(","):
                stripped_token = token.strip()
                if stripped_token:
                    skills_list.append(stripped_token)

        skills_text = sections.get("skills", "")
        if skills_text:
            vocab_matched = match_skills(skills_text)
            skills_list.extend(vocab_matched)

        seen_skills = set()
        deduped_skills = []
        for s in skills_list:
            s_lower = s.lower()
            if s_lower not in seen_skills:
                seen_skills.add(s_lower)
                deduped_skills.append(s)
        final_skills = sorted(deduped_skills)

        # STEP 4 — Extract experience_json
        experience_text = (
            sections.get("work experience") or
            sections.get("experience") or
            sections.get("employment") or ""
        )

        exp_lines = experience_text.splitlines()
        entry_blocks = []
        current_block = []
        for line in exp_lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue
            if EXP_DATE_PATTERN.search(stripped_line):
                if current_block:
                    entry_blocks.append(current_block)
                current_block = [stripped_line]
            else:
                if current_block:
                    current_block.append(stripped_line)
        if current_block:
            entry_blocks.append(current_block)

        experiences = []
        for block in entry_blocks:
            title_line = block[0]
            match = EXP_DATE_PATTERN.search(title_line)
            if not match:
                continue

            start_date = match.group(1)
            end_date = match.group(2)
            if end_date.lower() in ("present", "current"):
                end_date = "present"

            role_at_company = title_line[:match.start()].strip()
            at_match = re.search(r'\s+at\s+', role_at_company, re.IGNORECASE)
            if at_match:
                role = role_at_company[:at_match.start()].strip()
                company = role_at_company[at_match.end():].strip()
            else:
                role = role_at_company
                company = "Unknown"

            description = "\n".join(block[1:]).strip()
            experiences.append({
                "company": company,
                "role": role,
                "start_date": start_date,
                "end_date": end_date,
                "description": description
            })

        # STEP 5 — Extract education_json
        education_text = sections.get("education", "")

        DEGREE_KEYWORDS = {
            "phd": "PhD", "doctorate": "PhD",
            "master": "Master's", "m.sc": "Master's", "msc": "Master's", "mba": "MBA",
            "bachelor": "Bachelor's", "b.sc": "Bachelor's", "bsc": "Bachelor's",
            "b.tech": "Bachelor's", "btech": "Bachelor's", "b.e": "Bachelor's",
            "diploma": "Diploma", "associate": "Associate",
            "high school": "High School"
        }

        edu_lines = education_text.splitlines()
        edu_blocks = []
        current_edu_block = []
        for line in edu_lines:
            stripped = line.strip()
            if stripped:
                current_edu_block.append(stripped)
            else:
                if current_edu_block:
                    edu_blocks.append(current_edu_block)
                    current_edu_block = []
        if current_edu_block:
            edu_blocks.append(current_edu_block)

        educations = []
        for block in edu_blocks:
            block_text = "\n".join(block)
            block_text_lower = block_text.lower()

            degree = None
            for key, val in DEGREE_KEYWORDS.items():
                if key in block_text_lower:
                    degree = val
                    break

            year_match = EDU_DATE_PATTERN.search(block_text_lower)
            year = ""
            if year_match:
                start_y = year_match.group(1)
                end_y = year_match.group(2)
                if end_y.lower() == "present":
                    year = start_y
                else:
                    year = end_y
            else:
                fallback_match = EDU_YEAR_FALLBACK_PATTERN.search(block_text_lower)
                if fallback_match:
                    year = fallback_match.group(0)

            institution = "Unknown"
            for line in block:
                line_lower = line.lower()
                has_degree_kw = any(key in line_lower for key in DEGREE_KEYWORDS.keys())
                is_date_only = bool(ONLY_DATE_PATTERN.match(line_lower))
                # Skip long prose lines: more than 8 words or contains verbs typical of descriptions
                word_count = len(line.split())
                is_prose = word_count > 8 or re.search(
                    r'\b(experience|proficient|developing|working|developing|creating|using|with)\b',
                    line_lower
                )
                if not has_degree_kw and not is_date_only and not is_prose:
                    institution = line
                    break

            educations.append({
                "degree": degree or "Unknown",
                "institution": institution,
                "year": year or ""
            })

        # STEP 6 — Build and return ParsedCandidate
        return ParsedCandidate(
            name=name,
            email=email,
            phone=phone,
            skills=final_skills,
            experience_json=experiences,
            education_json=educations
        )
