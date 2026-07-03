import pytest
from unittest.mock import patch
from app.agents.matching_engine import MatchingEngineAgent, MatchResult
from app.agents.cv_parser import ParsedCandidate
from app.agents.jd_summarizer import ParsedJD
from app.config import settings

@pytest.fixture
def agent():
    return MatchingEngineAgent()

@pytest.fixture
def candidate():
    return ParsedCandidate(name="Bob", skills=["Python"], experience_json=[], education_json=[])

@pytest.fixture
def jd():
    return ParsedJD(required_skills=["Python"], min_experience_years=2, required_education="Bachelor's", responsibilities=[])

def test_successful_match(agent, candidate, jd):
    mock_json = """
    {
      "skill_score": 0.9,
      "experience_score": 0.8,
      "education_score": 1.0,
      "keyword_score": 0.7,
      "overall_score": 0.85
    }
    """
    with patch.object(MatchingEngineAgent, '_call_llm', return_value=mock_json):
        result = agent.run(candidate, jd)
        
    assert result.skill_score == 0.9
    assert result.experience_score == 0.8
    assert result.education_score == 1.0
    assert result.keyword_score == 0.7
    assert result.overall_score == 0.85
    # Assumes settings.MATCH_THRESHOLD is <= 0.85 (default is usually 0.8)
    assert result.is_shortlisted == (0.85 >= settings.MATCH_THRESHOLD)

def test_llm_failure_returns_zeros(agent, candidate, jd):
    with patch.object(MatchingEngineAgent, '_call_llm', side_effect=Exception("API Error")):
        result = agent.run(candidate, jd)
        
    assert result.overall_score == 0.0
    assert result.is_shortlisted is False

def test_invalid_json_returns_zeros(agent, candidate, jd):
    with patch.object(MatchingEngineAgent, '_call_llm', return_value="Invalid"):
        result = agent.run(candidate, jd)
        
    assert result.overall_score == 0.0
    assert result.is_shortlisted is False

def test_malformed_scores_returns_zeros(agent, candidate, jd):
    mock_json = """
    {
      "skill_score": "not a float",
      "overall_score": "bad"
    }
    """
    with patch.object(MatchingEngineAgent, '_call_llm', return_value=mock_json):
        result = agent.run(candidate, jd)
        
    assert result.overall_score == 0.0
    assert result.is_shortlisted is False
