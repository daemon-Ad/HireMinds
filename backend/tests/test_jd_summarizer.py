import pytest
from unittest.mock import patch
from app.agents.jd_summarizer import JDSummarizerAgent, ParsedJD

@pytest.fixture
def agent():
    return JDSummarizerAgent()

def test_successful_parse(agent):
    mock_json = """
    {
      "required_skills": ["Python", "AWS"],
      "min_experience_years": 5,
      "required_education": "Master's",
      "responsibilities": ["Lead team"]
    }
    """
    with patch.object(JDSummarizerAgent, '_call_llm', return_value=mock_json):
        result = agent.run("Senior Engineer", "Raw text")
        
    assert result.required_skills == ["Python", "AWS"]
    assert result.min_experience_years == 5
    assert result.required_education == "Master's"
    assert result.responsibilities == ["Lead team"]

def test_invalid_education_coerced_to_none(agent):
    mock_json = """
    {
      "required_education": "Some Fake Degree"
    }
    """
    with patch.object(JDSummarizerAgent, '_call_llm', return_value=mock_json):
        result = agent.run("Title", "Raw text")
        
    assert result.required_education == "None"

def test_llm_failure_triggers_regex_fallback(agent):
    # Regex fallback should find "5 years experience" and "PhD"
    raw_text = "We need 5 years of experience and a PhD in Computer Science."
    
    with patch.object(JDSummarizerAgent, '_call_llm', side_effect=Exception("API Error")):
        result = agent.run("Title", raw_text)
        
    assert result.min_experience_years == 5
    assert result.required_education == "PhD"
    assert result.required_skills == []

def test_invalid_json_triggers_regex_fallback(agent):
    raw_text = "Looking for 2 years experience and a Diploma."
    
    with patch.object(JDSummarizerAgent, '_call_llm', return_value="Bad JSON"):
        result = agent.run("Title", raw_text)
        
    assert result.min_experience_years == 2
    assert result.required_education == "Diploma"
