import pytest
from app.agents.cv_parser import CVParserAgent, ParsedCandidate


@pytest.fixture
def agent():
    return CVParserAgent()


SAMPLE_CV = """Candidate Resume (ID: C8810)
Name: Thomas Baird
Email: thomasbaird44@gmail.com
Phone: +1-605-1775
Education
Diploma in Software Engineering (2013-2015)
Hands-on experience in full-stack web development and mobile app creation.
Work Experience
Product Manager at DEF Ltd. (2017-2021)
Led cross-functional teams to develop innovative solutions, increasing product adoption by 40%.
Skills
Python & Machine Learning - Proficient in TensorFlow, PyTorch, and Scikit-learn with hands-on
experience in deploying AI solutions.
Certifications
Certified Ethical Hacker (CEH) - Demonstrated proficiency in ethical hacking, network security, and
vulnerability assessment.
Tech Stack
Python, TensorFlow, PyTorch, PostgreSQL, Docker, Kubernetes"""


# ── Name ───────────────────────────────────────────────────────────────────────

def test_extracts_name_with_prefix(agent):
    result = agent.run(SAMPLE_CV)
    assert result.name == "Thomas Baird"


def test_skips_resume_metadata_line(agent):
    result = agent.run(SAMPLE_CV)
    assert "Candidate Resume" not in result.name
    assert "C8810" not in result.name


def test_extracts_name_without_prefix(agent):
    cv = "Jane Smith\njanesmit@email.com\n+1-555-0000\nEducation\nBachelor's (2018-2022)"
    result = agent.run(cv)
    assert result.name == "Jane Smith"


def test_unknown_name_when_no_name_found(agent):
    cv = "thomasbaird44@gmail.com\n+1-605-1775\nEducation\nDiploma (2013-2015)"
    result = agent.run(cv)
    assert result.name == "Unknown"


# ── Email ──────────────────────────────────────────────────────────────────────

def test_extracts_email(agent):
    result = agent.run(SAMPLE_CV)
    assert result.email == "thomasbaird44@gmail.com"


def test_empty_email_when_absent(agent):
    cv = "John Doe\n+1-555-1234\nEducation\nBachelor's (2018-2022)"
    result = agent.run(cv)
    assert result.email == ""


# ── Phone ──────────────────────────────────────────────────────────────────────

def test_extracts_phone(agent):
    result = agent.run(SAMPLE_CV)
    assert result.phone is not None
    assert "605" in result.phone


def test_phone_none_when_absent(agent):
    cv = "John Doe\njohn@example.com\nEducation\nBachelor's (2018-2022)"
    result = agent.run(cv)
    assert result.phone is None


# ── Skills ─────────────────────────────────────────────────────────────────────

def test_extracts_skills_from_tech_stack(agent):
    result = agent.run(SAMPLE_CV)
    skill_lower = [s.lower() for s in result.skills]
    assert "python" in skill_lower
    assert "docker" in skill_lower
    assert "kubernetes" in skill_lower
    assert "postgresql" in skill_lower


def test_extracts_skills_from_vocab_matching(agent):
    result = agent.run(SAMPLE_CV)
    skill_lower = [s.lower() for s in result.skills]
    assert "machine learning" in skill_lower


def test_skills_are_deduplicated(agent):
    result = agent.run(SAMPLE_CV)
    skill_lower = [s.lower() for s in result.skills]
    assert skill_lower.count("python") == 1


def test_skills_are_sorted(agent):
    result = agent.run(SAMPLE_CV)
    assert result.skills == sorted(result.skills, key=str.lower)


def test_no_skills_returns_empty_list(agent):
    cv = "John Doe\njohn@example.com\nEducation\nBachelor's (2018-2022)"
    result = agent.run(cv)
    assert isinstance(result.skills, list)


# ── Experience ─────────────────────────────────────────────────────────────────

def test_extracts_single_experience_entry(agent):
    result = agent.run(SAMPLE_CV)
    assert len(result.experience_json) == 1


def test_experience_role_and_company(agent):
    result = agent.run(SAMPLE_CV)
    entry = result.experience_json[0]
    assert entry["role"] == "Product Manager"
    assert entry["company"] == "DEF Ltd."


def test_experience_dates(agent):
    result = agent.run(SAMPLE_CV)
    entry = result.experience_json[0]
    assert entry["start_date"] == "2017"
    assert entry["end_date"] == "2021"


def test_experience_present_end_date(agent):
    cv = """John Doe\njohn@example.com\nWork Experience\nSoftware Engineer at ACME Corp. (2020-present)\nBuilt APIs."""
    result = agent.run(cv)
    assert len(result.experience_json) == 1
    assert result.experience_json[0]["end_date"] == "present"


def test_experience_no_at_separator(agent):
    cv = """John Doe\njohn@example.com\nWork Experience\nFreelancer (2019-2022)\nDid various projects."""
    result = agent.run(cv)
    assert len(result.experience_json) == 1
    assert result.experience_json[0]["role"] == "Freelancer"
    assert result.experience_json[0]["company"] == "Unknown"


def test_multiple_experience_entries(agent):
    cv = """John Doe\njohn@example.com\nWork Experience
Senior Dev at Alpha Inc. (2020-2023)
Led backend team.
Junior Dev at Beta Ltd. (2017-2020)
Maintained legacy code."""
    result = agent.run(cv)
    assert len(result.experience_json) == 2
    assert result.experience_json[0]["company"] == "Alpha Inc."
    assert result.experience_json[1]["company"] == "Beta Ltd."


def test_no_experience_returns_empty_list(agent):
    cv = "John Doe\njohn@example.com\nEducation\nBachelor's (2018-2022)"
    result = agent.run(cv)
    assert result.experience_json == []


# ── Education ──────────────────────────────────────────────────────────────────

def test_extracts_diploma(agent):
    result = agent.run(SAMPLE_CV)
    assert len(result.education_json) == 1
    assert result.education_json[0]["degree"] == "Diploma"


def test_education_year(agent):
    result = agent.run(SAMPLE_CV)
    assert result.education_json[0]["year"] == "2015"


def test_detects_bachelors_degree(agent):
    cv = "Jane Smith\njane@email.com\nEducation\nBachelor's in Computer Science (2015-2019)"
    result = agent.run(cv)
    assert result.education_json[0]["degree"] == "Bachelor's"


def test_detects_masters_degree(agent):
    cv = "Jane Smith\njane@email.com\nEducation\nMaster's in Data Science (2019-2021)"
    result = agent.run(cv)
    assert result.education_json[0]["degree"] == "Master's"


def test_detects_phd(agent):
    cv = "Jane Smith\njane@email.com\nEducation\nPhD in AI (2019-2023)"
    result = agent.run(cv)
    assert result.education_json[0]["degree"] == "PhD"


def test_unknown_degree_when_not_found(agent):
    cv = "Jane Smith\njane@email.com\nEducation\nSome qualification (2015-2019)"
    result = agent.run(cv)
    assert result.education_json[0]["degree"] == "Unknown"


def test_no_education_returns_empty_list(agent):
    cv = "John Doe\njohn@example.com\nWork Experience\nDev at ACME (2019-2022)\nWrote code."
    result = agent.run(cv)
    assert result.education_json == []
