import pytest
from unittest.mock import patch
from datetime import datetime

from app.agents.matching_engine import MatchingEngineAgent, MatchResult
from app.agents.cv_parser import ParsedCandidate
from app.agents.jd_summarizer import ParsedJD


@pytest.fixture
def engine():
    return MatchingEngineAgent()


def make_candidate(**kwargs) -> ParsedCandidate:
    defaults = dict(
        name="Test Candidate",
        email="test@example.com",
        phone=None,
        skills=[],
        experience_json=[],
        education_json=[],
    )
    defaults.update(kwargs)
    return ParsedCandidate(**defaults)


def make_jd(**kwargs) -> ParsedJD:
    defaults = dict(
        required_skills=[],
        min_experience_years=0,
        required_education="None",
        responsibilities=[],
    )
    defaults.update(kwargs)
    return ParsedJD(**defaults)


# ── _score_skills ──────────────────────────────────────────────────────────────

def test_skill_score_perfect_match(engine):
    score = engine._score_skills(["python", "docker", "aws"], ["python", "docker", "aws"])
    assert score == 1.0


def test_skill_score_zero_overlap(engine):
    score = engine._score_skills(["java", "c++"], ["python", "docker"])
    assert score == 0.0


def test_skill_score_partial_match(engine):
    score = engine._score_skills(["python", "java"], ["python", "docker", "aws"])
    assert abs(score - 1/3) < 0.001


def test_skill_score_empty_required_returns_one(engine):
    score = engine._score_skills(["python", "docker"], [])
    assert score == 1.0


def test_skill_score_empty_candidate_returns_zero(engine):
    score = engine._score_skills([], ["python", "docker"])
    assert score == 0.0


def test_skill_score_case_insensitive(engine):
    score = engine._score_skills(["Python", "Docker"], ["python", "docker"])
    assert score == 1.0


def test_skill_score_candidate_superset(engine):
    # Candidate has MORE than required — score should cap at 1.0
    score = engine._score_skills(["python", "docker", "aws", "kubernetes"], ["python", "docker"])
    assert score == 1.0


# ── _score_experience ──────────────────────────────────────────────────────────

def test_experience_score_meets_requirement(engine):
    exp = [{"start_date": "2018", "end_date": "2023", "role": "Dev", "description": ""}]
    score = engine._score_experience(exp, min_experience_years=5)
    assert score == 1.0


def test_experience_score_exceeds_requirement(engine):
    exp = [{"start_date": "2015", "end_date": "2023", "role": "Dev", "description": ""}]
    score = engine._score_experience(exp, min_experience_years=5)
    assert score == 1.0


def test_experience_score_under_requirement(engine):
    exp = [{"start_date": "2021", "end_date": "2023", "role": "Dev", "description": ""}]
    score = engine._score_experience(exp, min_experience_years=4)
    assert abs(score - 0.5) < 0.001


def test_experience_score_zero_requirement_returns_one(engine):
    exp = [{"start_date": "2021", "end_date": "2023", "role": "Dev", "description": ""}]
    score = engine._score_experience(exp, min_experience_years=0)
    assert score == 1.0


def test_experience_score_no_experience_entries(engine):
    score = engine._score_experience([], min_experience_years=3)
    assert score == 0.0


def test_experience_present_end_date_uses_current_year(engine):
    current_year = datetime.now().year
    exp = [{"start_date": "2020", "end_date": "present", "role": "Dev", "description": ""}]
    total = engine._estimate_total_years(exp)
    assert total == current_year - 2020


def test_experience_current_end_date_treated_as_present(engine):
    current_year = datetime.now().year
    exp = [{"start_date": "2021", "end_date": "current", "role": "Dev", "description": ""}]
    total = engine._estimate_total_years(exp)
    assert total == current_year - 2021


def test_experience_multiple_entries_summed(engine):
    exp = [
        {"start_date": "2015", "end_date": "2018", "role": "Junior", "description": ""},
        {"start_date": "2018", "end_date": "2022", "role": "Senior", "description": ""},
    ]
    total = engine._estimate_total_years(exp)
    assert total == 7.0


def test_experience_bad_date_uses_fallback(engine):
    exp = [{"start_date": "unknown", "end_date": "unknown", "role": "Dev", "description": ""}]
    total = engine._estimate_total_years(exp)
    assert total == 1.5


# ── _score_education ───────────────────────────────────────────────────────────

def test_education_exact_match(engine):
    edu = [{"degree": "Bachelor's", "institution": "MIT", "year": "2020"}]
    score = engine._score_education(edu, "Bachelor's")
    assert score == 1.0


def test_education_exceeds_requirement(engine):
    edu = [{"degree": "PhD", "institution": "MIT", "year": "2020"}]
    score = engine._score_education(edu, "Bachelor's")
    assert score == 1.0


def test_education_one_level_below(engine):
    edu = [{"degree": "Diploma", "institution": "College", "year": "2018"}]
    score = engine._score_education(edu, "Bachelor's")
    assert score == 0.6


def test_education_two_levels_below(engine):
    edu = [{"degree": "High School", "institution": "School", "year": "2015"}]
    score = engine._score_education(edu, "Bachelor's")
    assert score == 0.2


def test_education_no_requirement_returns_one(engine):
    edu = [{"degree": "Diploma", "institution": "College", "year": "2018"}]
    score = engine._score_education(edu, "None")
    assert score == 1.0


def test_education_no_candidate_education(engine):
    score = engine._score_education([], "Bachelor's")
    assert score == 0.2


def test_education_takes_highest_degree(engine):
    edu = [
        {"degree": "Bachelor's", "institution": "Uni A", "year": "2016"},
        {"degree": "Master's",   "institution": "Uni B", "year": "2018"},
    ]
    score = engine._score_education(edu, "Master's")
    assert score == 1.0


# ── _score_keywords (TF-IDF) ──────────────────────────────────────────────────

def test_keyword_score_returns_float(engine):
    candidate = make_candidate(
        skills=["python", "fastapi"],
        experience_json=[{"role": "Backend Dev", "description": "built REST APIs with FastAPI"}],
    )
    jd = make_jd(
        required_skills=["python", "fastapi"],
        responsibilities=["Design and build REST APIs"],
    )
    score = engine._score_keywords(candidate, jd)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_keyword_score_empty_candidate_text(engine):
    candidate = make_candidate(skills=[], experience_json=[])
    jd = make_jd(required_skills=["python"], responsibilities=["Write code"])
    score = engine._score_keywords(candidate, jd)
    assert score == 0.0


def test_keyword_score_empty_jd_text(engine):
    candidate = make_candidate(skills=["python"])
    jd = make_jd(required_skills=[], responsibilities=[])
    score = engine._score_keywords(candidate, jd)
    assert score == 0.0


def test_keyword_score_identical_texts_high(engine):
    candidate = make_candidate(
        skills=["python", "docker"],
        experience_json=[{"role": "Dev", "description": "python docker deployment"}],
    )
    jd = make_jd(
        required_skills=["python", "docker"],
        responsibilities=["python docker deployment"],
    )
    score = engine._score_keywords(candidate, jd)
    assert score > 0.5


# ── run() full integration ─────────────────────────────────────────────────────

def test_run_returns_match_result(engine):
    candidate = make_candidate(skills=["python"])
    jd = make_jd(required_skills=["python"])
    result = engine.run(candidate, jd)
    assert isinstance(result, MatchResult)


def test_run_weights_sum_correctly(engine):
    """Verify the weighted formula: 0.4+0.3+0.2+0.1 = 1.0."""
    candidate = make_candidate(
        skills=["python", "docker"],
        experience_json=[{"start_date": "2018", "end_date": "2022", "role": "Dev", "description": "python"}],
        education_json=[{"degree": "Bachelor's", "institution": "Uni", "year": "2018"}],
    )
    jd = make_jd(
        required_skills=["python", "docker"],
        min_experience_years=4,
        required_education="Bachelor's",
        responsibilities=["Build python services"],
    )
    result = engine.run(candidate, jd)
    expected = round(
        0.40 * result.skill_score
        + 0.30 * result.experience_score
        + 0.20 * result.education_score
        + 0.10 * result.keyword_score,
        4,
    )
    assert result.overall_score == expected


def test_run_shortlisted_above_threshold(engine):
    candidate = make_candidate(
        skills=["python", "docker", "aws", "fastapi", "postgresql"],
        experience_json=[{"start_date": "2015", "end_date": "2023", "role": "Senior Dev", "description": "python fastapi rest api"}],
        education_json=[{"degree": "Bachelor's", "institution": "MIT", "year": "2015"}],
    )
    jd = make_jd(
        required_skills=["python", "docker"],
        min_experience_years=3,
        required_education="Bachelor's",
        responsibilities=["Build REST APIs with FastAPI"],
    )
    result = engine.run(candidate, jd)
    assert result.is_shortlisted is True


def test_run_not_shortlisted_below_threshold(engine):
    candidate = make_candidate(
        skills=["html", "css"],
        experience_json=[{"start_date": "2022", "end_date": "2023", "role": "Intern", "description": "made websites"}],
        education_json=[{"degree": "High School", "institution": "School", "year": "2021"}],
    )
    jd = make_jd(
        required_skills=["python", "docker", "kubernetes"],
        min_experience_years=5,
        required_education="Bachelor's",
        responsibilities=["Build backend systems in python"],
    )
    result = engine.run(candidate, jd)
    assert result.is_shortlisted is False


def test_run_all_scores_between_zero_and_one(engine):
    candidate = make_candidate(skills=["python"])
    jd = make_jd(required_skills=["python", "docker"])
    result = engine.run(candidate, jd)
    for score in [result.skill_score, result.experience_score, result.education_score, result.keyword_score, result.overall_score]:
        assert 0.0 <= score <= 1.0, f"Score out of range: {score}"
