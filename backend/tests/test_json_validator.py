import pytest
from app.utils.json_validator import parse_llm_response


def test_clean_json_parses():
    raw = '{"name": "Alice", "score": 95}'
    result = parse_llm_response(raw)
    assert result == {"name": "Alice", "score": 95}


def test_json_fenced_with_language_tag():
    raw = '```json\n{"name": "Alice", "score": 95}\n```'
    result = parse_llm_response(raw)
    assert result == {"name": "Alice", "score": 95}


def test_json_fenced_without_language_tag():
    raw = '```\n{"name": "Alice"}\n```'
    result = parse_llm_response(raw)
    assert result == {"name": "Alice"}


def test_malformed_json_returns_none():
    raw = '{"name": "Alice", "score":}'
    result = parse_llm_response(raw)
    assert result is None


def test_non_dict_json_returns_none():
    raw = '[1, 2, 3]'
    result = parse_llm_response(raw)
    assert result is None


def test_empty_string_returns_none():
    result = parse_llm_response("")
    assert result is None


def test_whitespace_only_returns_none():
    result = parse_llm_response("   \n  ")
    assert result is None


def test_nested_json_parses():
    raw = '{"skills": ["python", "docker"], "years": 5}'
    result = parse_llm_response(raw)
    assert result["skills"] == ["python", "docker"]
    assert result["years"] == 5
