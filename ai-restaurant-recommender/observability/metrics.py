"""
Prometheus metrics for the AI Restaurant Recommendation Service.
"""

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response


REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)
LLM_CALL_COUNT = Counter(
    "llm_calls_total",
    "Total LLM API calls",
    ["status"],
)
LLM_LATENCY = Histogram(
    "llm_call_duration_seconds",
    "LLM call latency in seconds",
    buckets=(0.5, 1.0, 2.0, 3.0, 5.0, 10.0),
)
ERROR_COUNT = Counter(
    "errors_total",
    "Total errors",
    ["type"],
)


def get_metrics_response() -> Response:
    """Return Prometheus metrics in text format."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
