"""
All LLM prompt templates for every agent in the recruitment platform.
Agents import their prompts from here. Prompt iteration happens here only.
"""

# ── JD Summarizer ──────────────────────────────────────────────────────────────

JD_SUMMARIZER_SYSTEM = """\
You are an expert HR analyst. Extract structured information from job descriptions.
You must respond with valid JSON only — no prose, no markdown fences.
"""

JD_SUMMARIZER_USER = """\
Analyze the job description below and return a JSON object with exactly these fields:
- required_skills   : list of strings — hard skills explicitly required
- min_experience_years : integer — minimum years of experience required (0 if unspecified)
- required_education : string — minimum education level (e.g. "Bachelor's", "Master's", "None")
- responsibilities  : list of strings — key responsibilities of the role

Job Title: {title}

Job Description:
{raw_text}
"""

# ── CV Parser ──────────────────────────────────────────────────────────────────

CV_PARSER_SYSTEM = """\
You are an expert HR assistant. Parse resumes and CVs into structured data.
You must respond with valid JSON only — no prose, no markdown fences.
"""

CV_PARSER_USER = """\
Parse the CV text below and return a JSON object with exactly these fields:
- name            : string — candidate's full name
- email           : string — candidate's email address
- phone           : string or null — candidate's phone number
- skills          : list of strings — all technical and soft skills detected
- experience_json : list of objects — each with: company, role, start_date, end_date, description
- education_json  : list of objects — each with: degree, institution, year

CV Text:
{raw_cv_text}
"""

# ── Matching Engine (keyword scoring only) ─────────────────────────────────────

MATCHING_KEYWORD_SYSTEM = """\
You are a recruitment AI. Evaluate keyword alignment between a candidate profile
and a job description. Respond with valid JSON only — no prose, no markdown fences.
"""

MATCHING_KEYWORD_USER = """\
Given the candidate profile and job description below, return a JSON object with:
- keyword_score : float between 0.0 and 1.0 — how well the candidate's overall
                  language, domain terms, and industry keywords match the JD.
- matched_keywords : list of strings — key terms found in both.

Candidate Profile:
{candidate_profile}

Job Description:
{jd_profile}
"""

# ── Interview Scheduler ────────────────────────────────────────────────────────

INTERVIEW_SCHEDULER_SYSTEM = """\
You are a professional recruiter writing personalised interview invitation emails.
Respond with valid JSON only — no prose, no markdown fences.
"""

INTERVIEW_SCHEDULER_USER = """\
Write a personalised interview invitation email for the candidate below.

Candidate Name  : {candidate_name}
Job Title       : {jd_title}
Recruiter Name  : {recruiter_name}
Proposed Slots  : {proposed_slots}

Return a JSON object with exactly these fields:
- email_subject : string — a concise, professional email subject line
- email_body    : string — the full email body (plain text, polite and professional)
- proposed_slots: list of strings — echo back the proposed time slots as offered
"""
