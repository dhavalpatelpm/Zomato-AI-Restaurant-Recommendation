"""
Tests for Phase 5: Response Formatting & Ranking Layer.
Uses synthetic test data. No Groq or Phase 3 API calls.
"""

from datetime import datetime

import pandas as pd
import pytest

from src.phase5_response_layer import build_final_response
from src.phase5_response_layer.confidence import compute_confidence_score
from src.phase5_response_layer.formatter import format_final_response
from src.phase5_response_layer.ranker import apply_ranking
from src.phase5_response_layer.schemas import FinalResponse, RecommendationItem


def _sample_llm_output():
    return {
        "recommendations": [
            {"restaurant_name": "Cafe B", "reason": "Good food", "rating": "4.2", "price_range": "400"},
            {"restaurant_name": "Cafe A", "reason": "Best match", "rating": "4.6", "price_range": "300"},
            {"restaurant_name": "Cafe C", "reason": "Nice ambiance", "rating": "3.8", "price_range": "500"},
        ]
    }


def _sample_filtered_df():
    return pd.DataFrame({
        "restaurant_name": ["Cafe A", "Cafe B", "Cafe C"],
        "locality": ["x", "x", "x"],
        "rating": [4.6, 4.2, 3.8],
        "price_range": [300, 400, 500],
        "high_rated_flag": [True, True, False],
    })


def test_ranking_sorts_correctly():
    """Higher-rated, lower-price, high_rated items rank first."""
    llm_out = _sample_llm_output()
    df = _sample_filtered_df()
    ranked = apply_ranking(llm_out, df)
    assert len(ranked) == 3
    assert ranked[0]["restaurant_name"] == "Cafe A"
    assert ranked[0]["rating"] == 4.6


def test_confidence_score_between_0_and_1():
    """Confidence score is in [0, 1] range."""
    rec = {"restaurant_name": "Cafe A", "reason": "x", "rating": 4.6, "price_range": 400}
    df = _sample_filtered_df()
    score = compute_confidence_score(rec, df)
    assert 0.0 <= score <= 1.0
    assert round(score, 2) == score


def test_formatter_adds_timestamp():
    """Formatter adds generated_at timestamp."""
    ranked = [
        {"restaurant_name": "A", "reason": "Good", "rating": 4.5, "price_range": 300, "confidence_score": 0.8},
    ]
    result = format_final_response(ranked)
    assert hasattr(result, "generated_at")
    assert isinstance(result.generated_at, datetime)


def test_response_schema_validates_properly():
    """FinalResponse schema validates all required fields."""
    ranked = [
        {"restaurant_name": "Cafe X", "reason": "Excellent", "rating": 4.5, "price_range": 350, "confidence_score": 0.85},
    ]
    result = format_final_response(ranked)
    assert result.total_results == 1
    assert result.recommendations[0].restaurant_name == "Cafe X"
    assert result.recommendations[0].confidence_score == 0.85


def test_empty_recommendations_handled_gracefully():
    """Empty LLM output returns valid empty response."""
    result = build_final_response({"recommendations": []}, pd.DataFrame())
    assert result.total_results == 0
    assert result.recommendations == []
    assert isinstance(result.generated_at, datetime)


def test_missing_optional_fields_handled_safely():
    """Missing reason gets default; rating/price normalized."""
    ranked = [
        {"restaurant_name": "X", "reason": "", "rating": "4.5", "price_range": "400", "confidence_score": 0.7},
    ]
    result = format_final_response(ranked)
    assert result.recommendations[0].reason != ""
    assert result.recommendations[0].rating == 4.5
    assert result.recommendations[0].price_range == 400


def test_deterministic_ranking_same_input_same_output():
    """Same input produces same ranked output."""
    llm_out = _sample_llm_output()
    df = _sample_filtered_df()
    r1 = apply_ranking(llm_out, df)
    r2 = apply_ranking(llm_out, df)
    assert [x["restaurant_name"] for x in r1] == [x["restaurant_name"] for x in r2]
