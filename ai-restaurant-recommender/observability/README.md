# AI Restaurant Recommendation Service – Observability

Monitoring, logging, and metrics for the AI Restaurant Recommendation Service.

## Enabling Monitoring

Observability is enabled automatically when the `observability` module is importable. The FastAPI app loads:

- Request logging middleware
- Prometheus metrics at `/metrics`
- Readiness probe at `/ready`
- Structured JSON logging

Ensure the backend runs with `observability` on the Python path (default when running from `ai-restaurant-recommender`).

## Running Prometheus and Grafana

From the `ai-restaurant-recommender` directory:

```bash
docker compose -f observability/docker-compose.monitoring.yml up -d
```

Or from the project root:

```bash
docker compose -f ai-restaurant-recommender/observability/docker-compose.monitoring.yml up -d
```

## Accessing Dashboards

- **Prometheus**: http://localhost:9090  
  - Query metrics, e.g. `rate(http_requests_total[5m])`
- **Grafana**: http://localhost:3001  
  - Default login: admin / admin  
  - Add Prometheus as a data source: `http://host.docker.internal:9090` (or `http://prometheus:9090` if in same compose network)

## Prometheus Scrape Config

Update `observability/prometheus.yml` so the `targets` list points to your backend. Examples:

- Local: `["localhost:8000"]`
- Docker: `["host.docker.internal:8000"]`
- Compose: `["backend:8000"]`

## Available Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests by method, endpoint, status |
| `http_request_duration_seconds` | Histogram | Request latency |
| `llm_calls_total` | Counter | LLM API calls by status (success/error) |
| `llm_call_duration_seconds` | Histogram | LLM call latency |
| `errors_total` | Counter | Errors by type |

## Log Structure

Logs are emitted as JSON with fields:

- `timestamp`: ISO 8601 UTC
- `level`: INFO, WARNING, ERROR
- `service_name`: ai-restaurant-recommender
- `message`: Log message
- `request_id`: Per-request ID (when present)
- `path`: Request path (when present)
- `latency_ms`: Request duration in ms (when present)
