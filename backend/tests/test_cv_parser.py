import pytest
from unittest.mock import patch
from app.agents.cv_parser import CVParserAgent, ParsedCandidate

@pytest.fixture
def agent():
    return CVParserAgent()

def test_successful_parse(agent):
    mock_json = """
    {
      "name": "Jane Doe",
      "email": "jane@example.com",
      "phone": "555-1234",
      "skills": ["Python", "FastAPI"],
      "experience_json": [{"role": "Dev"}],
      "education_json": [{"degree": "BSc"}]
    }
    """
    with patch.object(CVParserAgent, '_call_llm', return_value=mock_json):
        result = agent.run("Raw CV Text")
        
    assert result.name == "Jane Doe"
    assert result.email == "jane@example.com"
    assert result.phone == "555-1234"
    assert result.skills == ["Python", "FastAPI"]
    assert len(result.experience_json) == 1
    assert len(result.education_json) == 1

def test_missing_fields_defaults(agent):
    mock_json = """{"name": "John"}"""
    with patch.object(CVParserAgent, '_call_llm', return_value=mock_json):
        result = agent.run("Raw CV Text")
        
    assert result.name == "John"
    assert result.email == ""
    assert result.phone is None
    assert result.skills == []
    assert result.experience_json == []
    assert result.education_json == []

def test_llm_failure_returns_empty(agent):
    with patch.object(CVParserAgent, '_call_llm', side_effect=Exception("API Error")):
        result = agent.run("Raw CV Text")
        
    assert result.name == "Unknown"
    assert result.email == ""
    assert result.skills == []

def test_invalid_json_returns_empty(agent):
    with patch.object(CVParserAgent, '_call_llm', return_value="This is not JSON"):
        result = agent.run("Raw CV Text")
        
    assert result.name == "Unknown"
    assert result.email == ""
    assert result.skills == []
