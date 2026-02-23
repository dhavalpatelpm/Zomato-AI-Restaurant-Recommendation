"""
Request/response logging middleware for FastAPI.
"""

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .metrics import REQUEST_COUNT, REQUEST_LATENCY


logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"


def _normalize_path(path: str) -> str:
    """Normalize path for metrics (avoid high cardinality)."""
    if path.startswith("/api/"):
        return "/api/*"
    return path or "/"


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs requests and attaches request_id."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        start = time.perf_counter()
        path = _normalize_path(request.url.path)

        response = await call_next(request)

        latency = time.perf_counter() - start
        latency_ms = latency * 1000
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=path,
            status=str(response.status_code),
        ).inc()
        REQUEST_LATENCY.labels(method=request.method, endpoint=path).observe(latency)

        log_record = logger.makeRecord(
            logger.name,
            logging.INFO,
            __file__,
            0,
            f"{request.method} {request.url.path} {response.status_code} {latency_ms:.2f}ms",
            (),
            None,
        )
        log_record.request_id = request_id
        log_record.path = request.url.path
        log_record.latency_ms = round(latency_ms, 2)
        logger.handle(log_record)

        response.headers[REQUEST_ID_HEADER] = request_id
        return response
