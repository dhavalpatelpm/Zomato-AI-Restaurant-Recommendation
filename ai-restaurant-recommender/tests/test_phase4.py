"""
Tests for Phase 4: LLM Recommendation Engine.
Uses mocked Groq client. No external API calls.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.phase4_llm_engine import generate_recommendations
from src.phase4_llm_engine.prompt_builder import build_recommendation_prompt
from src.phase4_llm_engine.response_parser import parse_llm_response, LLMResponseParseError
from src.phase4_llm_engine.config import get_groq_api_key


def test_prompt_builder_generates_valid_structured_prompt():
    """Prompt builder produces prompt with user prefs and restaurants."""
    prefs = {"locality": "koramangala", "price_range": 500, "min_rating": 4.0, "cuisines": ["north indian"]}
    restaurants = [
        {"restaurant_name": "A", "locality": "koramangala", "cuisines": "North Indian", "price_range": 400, "rating": 4.2},
    ]
    prompt = build_recommendation_prompt(prefs, restaurants)
    assert isinstance(prompt, str)
    assert "koramangala" in prompt
    assert "500" in prompt
    assert "north indian" in prompt
    assert "A" in prompt
    assert "recommendations" in prompt
    assert "restaurant_name" in prompt
    assert "reason" in prompt


def test_response_parser_correctly_parses_valid_json():
    """Parser returns structured dict for valid JSON."""
    response = '{"recommendations": [{"restaurant_name": "Cafe A", "reason": "Great food", "rating": "4.5", "price_range": "400"}]}'
    parsed = parse_llm_response(response)
    assert "recommendations" in parsed
    assert len(parsed["recommendations"]) == 1
    rec = parsed["recommendations"][0]
    assert rec["restaurant_name"] == "Cafe A"
    assert rec["reason"] == "Great food"
    assert rec["rating"] == "4.5"
    assert rec["price_range"] == "400"


def test_response_parser_raises_error_on_invalid_json():
    """Parser raises LLMResponseParseError for invalid JSON."""
    with pytest.raises(LLMResponseParseError, match="Invalid JSON|empty"):
        parse_llm_response("not json {{{")
    with pytest.raises(LLMResponseParseError, match="empty"):
        parse_llm_response("")
    with pytest.raises(LLMResponseParseError, match="recommendations"):
        parse_llm_response('{"foo": "bar"}')
    with pytest.raises(LLMResponseParseError, match="restaurant_name"):
        parse_llm_response('{"recommendations": [{"reason": "x", "rating": "4", "price_range": "100"}]}')


def test_llm_service_pipeline_works_when_groq_mocked():
    """LLM service returns parsed recommendations when Groq is mocked."""
    mock_response = '{"recommendations": [{"restaurant_name": "Test Cafe", "reason": "Best match", "rating": "4.5", "price_range": "300"}]}'
    prefs = {"locality": "koramangala", "price_range": 500, "min_rating": 4.0, "cuisines": []}
    restaurants = [{"restaurant_name": "Test Cafe", "locality": "koramangala", "cuisines": "Indian", "price_range": 300, "rating": 4.5}]

    with patch("src.phase4_llm_engine.llm_service.call_groq_llm", return_value=mock_response):
        result = generate_recommendations(prefs, restaurants)

    assert "recommendations" in result
    assert len(result["recommendations"]) == 1
    assert result["recommendations"][0]["restaurant_name"] == "Test Cafe"
    assert result["recommendations"][0]["reason"] == "Best match"


def test_missing_api_key_raises_exception():
    """get_groq_api_key raises ValueError when GROQ_API_KEY not set."""
    with patch("src.phase4_llm_engine.config.os.getenv", return_value=""):
        with pytest.raises(ValueError, match="GROQ_API_KEY"):
            get_groq_api_key()
