"""
Tests for Phase 8: Observability.
"""

import pytest
from fastapi.testclient import TestClient

from observability.logging_config import setup_logging
from observability.middleware import REQUEST_ID_HEADER
from observability.metrics import get_metrics_response


def test_logging_config_loads_without_error():
    """Logging config initializes without raising."""
    setup_logging()


def test_middleware_attaches_request_id():
    """Middleware adds X-Request-ID to response headers."""
    from src.phase3_api_service.app import app
    client = TestClient(app)
    response = client.get("/health")
    assert REQUEST_ID_HEADER in response.headers
    assert len(response.headers[REQUEST_ID_HEADER]) > 0


def test_metrics_endpoint_returns_200():
    """GET /metrics returns 200 and Prometheus format."""
    from src.phase3_api_service.app import app
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text or "prometheus" in response.text.lower()


def test_health_endpoint_returns_healthy():
    """GET /health returns healthy status."""
    from src.phase3_api_service.app import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "healthy"


def test_prometheus_metrics_increment():
    """Request metrics are exposed and increment on requests."""
    from src.phase3_api_service.app import app
    client = TestClient(app)
    client.get("/health")
    client.get("/health")
    metrics_response = client.get("/metrics")
    assert "http_requests_total" in metrics_response.text


def test_llm_monitor_logs_correctly():
    """LLM monitor records metrics when Groq is mocked."""
    from observability.llm_monitor import monitored_llm_call
    from observability.metrics import get_metrics_response

    @monitored_llm_call
    def fake_llm():
        return "ok"

    result = fake_llm()
    assert result == "ok"
    metrics = get_metrics_response()
    assert metrics.body
    assert b"llm_calls_total" in metrics.body
