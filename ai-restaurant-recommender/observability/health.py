"""
Health and readiness probe endpoints.
"""

import logging

from fastapi import APIRouter


logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


def _check_groq_key() -> bool:
    """Verify GROQ_API_KEY is present."""
    try:
        from src.phase3_api_service.config import get_groq_api_key
        key = get_groq_api_key()
        return bool(key and key.strip())
    except Exception:
        return False


def _check_dataset_loaded() -> bool:
    """Verify dataset can be loaded (lightweight check)."""
    try:
        from src.phase3_api_service.service import _load_processed_dataset
        df = _load_processed_dataset()
        return df is not None and len(df) > 0
    except Exception:
        return False


@router.get("/ready")
def ready() -> dict:
    """Readiness probe: application is ready to serve traffic."""
    groq_ok = _check_groq_key()
    dataset_ok = _check_dataset_loaded()
    ready_status = groq_ok and dataset_ok
    return {
        "status": "ready" if ready_status else "not_ready",
        "checks": {
            "groq_api_key": groq_ok,
            "dataset_loaded": dataset_ok,
        },
    }
