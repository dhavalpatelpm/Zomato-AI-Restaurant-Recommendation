"""
Integration tests: Phase 3 -> Phase 4 -> Phase 5 pipeline.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


@patch("src.phase4_llm_engine.groq_client.call_groq_llm")
def test_recommend_endpoint_full_pipeline(mock_groq):
    """Recommend endpoint returns LLM-enhanced results when Groq is available."""
    mock_groq.return_value = '''{"recommendations": [
        {"restaurant_name": "Test Cafe", "reason": "Great match", "rating": "4.5", "price_range": "400"}
    ]}'''

    from src.phase3_api_service.app import app
    client = TestClient(app)

    response = client.post(
        "/api/recommend",
        json={
            "locality": "koramangala",
            "price_range": 500,
            "min_rating": 4.0,
            "cuisines": ["North Indian"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert data["total_results"] >= 0
    assert "generated_at" in data
    if data["recommendations"]:
        rec = data["recommendations"][0]
        assert "restaurant_name" in rec
        assert "reason" in rec
        assert "confidence_score" in rec


def test_recommend_endpoint_fallback_when_empty():
    """Recommend endpoint returns empty list for unknown locality."""
    from src.phase3_api_service.app import app
    client = TestClient(app)

    response = client.post(
        "/api/recommend",
        json={
            "locality": "nonexistent_locality_xyz",
            "price_range": 500,
            "min_rating": 4.0,
            "cuisines": [],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["recommendations"] == []
    assert data["total_results"] == 0
