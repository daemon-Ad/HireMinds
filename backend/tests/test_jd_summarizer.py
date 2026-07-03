import pytest
from app.agents.jd_summarizer import JDSummarizerAgent, ParsedJD


@pytest.fixture
def agent():
    return JDSummarizerAgent()


# ── Skills ─────────────────────────────────────────────────────────────────────

def test_extracts_known_skills(agent):
    text = "We need Python, Docker, and PostgreSQL experience."
    result = agent.run(title="Dev", raw_text=text)
    skills_lower = [s.lower() for s in result.required_skills]
    assert "python" in skills_lower
    assert "docker" in skills_lower
    assert "postgresql" in skills_lower


def test_no_skills_returns_empty(agent):
    text = "Looking for a great communicator who loves teamwork."
    result = agent.run(title="Manager", raw_text=text)
    assert isinstance(result.required_skills, list)


def test_skills_are_deduplicated(agent):
    text = "Python developer. Must know Python and python scripting."
    result = agent.run(title="Dev", raw_text=text)
    skill_lower = [s.lower() for s in result.required_skills]
    assert skill_lower.count("python") == 1


# ── Experience ─────────────────────────────────────────────────────────────────

def test_extracts_years_of_experience(agent):
    result = agent.run(title="Dev", raw_text="Requires 5 years of experience in backend.")
    assert result.min_experience_years == 5


def test_extracts_minimum_years(agent):
    result = agent.run(title="Dev", raw_text="Minimum 3 years in data science required.")
    assert result.min_experience_years == 3


def test_extracts_at_least_pattern(agent):
    result = agent.run(title="Dev", raw_text="At least 7 years of software development.")
    assert result.min_experience_years == 7


def test_takes_max_when_multiple_experience_numbers(agent):
    result = agent.run(title="Dev", raw_text="3 years of frontend experience and 6 years of backend experience required.")
    assert result.min_experience_years == 6


def test_no_experience_mentioned_returns_zero(agent):
    result = agent.run(title="Dev", raw_text="Looking for a passionate developer.")
    assert result.min_experience_years == 0


# ── Education ──────────────────────────────────────────────────────────────────

def test_detects_bachelors(agent):
    result = agent.run(title="Dev", raw_text="Bachelor's degree in Computer Science required.")
    assert result.required_education == "Bachelor's"


def test_detects_masters(agent):
    result = agent.run(title="Dev", raw_text="Master's degree or equivalent required.")
    assert result.required_education == "Master's"


def test_detects_phd(agent):
    result = agent.run(title="Researcher", raw_text="PhD in Machine Learning or related field.")
    assert result.required_education == "PhD"


def test_detects_diploma(agent):
    result = agent.run(title="Tech", raw_text="Diploma in IT or equivalent experience.")
    assert result.required_education == "Diploma"


def test_no_education_returns_none_string(agent):
    result = agent.run(title="Dev", raw_text="We just need someone who can code well.")
    assert result.required_education == "None"


def test_phd_takes_priority_over_bachelors(agent):
    result = agent.run(title="Researcher", raw_text="PhD preferred; Bachelor's minimum.")
    assert result.required_education == "PhD"


# ── Responsibilities ───────────────────────────────────────────────────────────

def test_extracts_bullets_when_header_present(agent):
    text = """
Responsibilities:
- Design and build REST APIs
- Manage PostgreSQL databases
- Deploy with Docker
"""
    result = agent.run(title="Dev", raw_text=text)
    assert len(result.responsibilities) >= 1
    assert any("api" in r.lower() or "rest" in r.lower() for r in result.responsibilities)


def test_extracts_action_sentences_without_header(agent):
    text = "You will design scalable APIs. We expect you to manage deployments. The team will collaborate daily."
    result = agent.run(title="Dev", raw_text=text)
    assert len(result.responsibilities) >= 1


def test_responsibilities_capped_at_five(agent):
    text = """
Responsibilities:
- Task one that needs doing
- Task two that needs doing
- Task three that needs doing
- Task four that needs doing
- Task five that needs doing
- Task six that needs doing
- Task seven that needs doing
"""
    result = agent.run(title="Dev", raw_text=text)
    assert len(result.responsibilities) <= 5


def test_empty_text_returns_empty_responsibilities(agent):
    result = agent.run(title="Dev", raw_text="")
    assert result.responsibilities == []
