"""
Phase 5 Response Layer: Response normalization and schema formatting.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .schemas import FinalResponse, RecommendationItem


logger = logging.getLogger(__name__)

DEFAULT_REASON = "Recommended based on your preferences."
DEFAULT_RATING = 4.0
DEFAULT_PRICE = 0


def _safe_float(val: Any, default: float = 0.0) -> float:
    if val is None or val == "":
        return default
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _safe_int(val: Any, default: int = 0) -> int:
    if val is None or val == "":
        return default
    try:
        return int(float(val))
    except (TypeError, ValueError):
        return default


def format_final_response(
    ranked_recommendations: List[Dict[str, Any]],
    generated_at: Optional[datetime] = None,
) -> FinalResponse:
    """
    Format ranked recommendations into FinalResponse schema.

    Normalizes types, ensures required fields, adds timestamp.

    Args:
        ranked_recommendations: List of ranked recommendation dicts with confidence_score.
        generated_at: Optional timestamp; defaults to now.

    Returns:
        Validated FinalResponse Pydantic model.
    """
    items = []
    for rec in ranked_recommendations:
        reason = str(rec.get("reason", "")).strip()
        if not reason:
            reason = DEFAULT_REASON

        rating = _safe_float(rec.get("rating"), DEFAULT_RATING)
        rating = min(5.0, max(0.0, rating))

        price = _safe_int(rec.get("price_range"), DEFAULT_PRICE)
        price = max(0, price)

        confidence = _safe_float(rec.get("confidence_score", 0.5), 0.5)
        confidence = min(1.0, max(0.0, confidence))

        name = str(rec.get("restaurant_name", "")).strip()
        if not name:
            continue

        items.append(
            RecommendationItem(
                restaurant_name=name,
                rating=round(rating, 1),
                price_range=price,
                reason=reason,
                confidence_score=round(confidence, 2),
            )
        )

    ts = generated_at or datetime.utcnow()
    logger.info("Formatted %d recommendations into FinalResponse", len(items))
    return FinalResponse(
        recommendations=items,
        total_results=len(items),
        generated_at=ts,
    )
