"""
LLM call monitoring and metrics.
"""

import logging
import time
from typing import Callable, TypeVar

from .metrics import ERROR_COUNT, LLM_CALL_COUNT, LLM_LATENCY


logger = logging.getLogger(__name__)

T = TypeVar("T")


def monitored_llm_call(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to monitor LLM calls with metrics and structured logging."""

    def wrapper(*args, **kwargs) -> T:
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            latency = time.perf_counter() - start
            LLM_CALL_COUNT.labels(status="success").inc()
            LLM_LATENCY.observe(latency)
            logger.info(
                "LLM call completed",
                extra={
                    "response_time_seconds": round(latency, 3),
                    "status": "success",
                },
            )
            return result
        except Exception as e:
            latency = time.perf_counter() - start
            LLM_CALL_COUNT.labels(status="error").inc()
            LLM_LATENCY.observe(latency)
            ERROR_COUNT.labels(type="llm").inc()
            logger.warning(
                "LLM call failed: %s",
                str(e),
                extra={
                    "response_time_seconds": round(latency, 3),
                    "status": "error",
                },
            )
            raise

    return wrapper
