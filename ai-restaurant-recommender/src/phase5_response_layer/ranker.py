"""
Phase 5 Response Layer: Deterministic ranking logic.
"""

import logging
from typing import Any, Dict, List

import pandas as pd


logger = logging.getLogger(__name__)

RATING_WEIGHT = 0.6
HIGH_RATED_WEIGHT = 0.2
PRICE_WEIGHT = 0.2


def _safe_float(val: Any, default: float = 0.0) -> float:
    """Convert value to float safely."""
    if val is None or val == "":
        return default
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _safe_int(val: Any, default: int = 0) -> int:
    """Convert value to int safely."""
    if val is None or val == "":
        return default
    try:
        return int(float(val))
    except (TypeError, ValueError):
        return default


def _normalize_restaurant_name(name: str) -> str:
    """Normalize for matching."""
    return str(name).strip().lower()


def apply_ranking(
    llm_output: Dict[str, Any],
    filtered_restaurants_df: pd.DataFrame,
) -> List[Dict[str, Any]]:
    """
    Apply deterministic ranking to LLM recommendations.

    Cross-references LLM output with dataset and scores by:
    score = (rating_norm * 0.6) + (high_rated_flag * 0.2) + (normalized_price_score * 0.2)

    Args:
        llm_output: Dict with 'recommendations' list from Phase 4.
        filtered_restaurants_df: DataFrame from Phase 3 filtering.

    Returns:
        Ranked list of recommendation dicts.
    """
    recs = llm_output.get("recommendations", [])
    if not recs:
        logger.info("No recommendations to rank")
        return []

    if filtered_restaurants_df.empty:
        recs_sorted = sorted(
            recs,
            key=lambda r: _safe_float(r.get("rating", 0)),
            reverse=True,
        )
        return recs_sorted

    df = filtered_restaurants_df.copy()
    df["_name_norm"] = df["restaurant_name"].astype(str).str.strip().str.lower()
    name_to_row = df.set_index("_name_norm").to_dict("index")

    max_price = df["price_range"].max()
    if max_price <= 0:
        max_price = 1

    scored = []
    for item in recs:
        name = _normalize_restaurant_name(item.get("restaurant_name", ""))
        row = name_to_row.get(name)

        rating = _safe_float(item.get("rating", 0), 0.0)
        price = _safe_int(item.get("price_range", 0), 0)

        if row is not None:
            rating = float(row.get("rating", rating))
            price = int(row.get("price_range", price))
            high_rated = 1.0 if row.get("high_rated_flag", False) else 0.0
            item = {**item, "rating": rating, "price_range": price}
        else:
            high_rated = 1.0 if rating >= 4.0 else 0.0

        rating_norm = min(rating / 5.0, 1.0)
        price_norm = max(0.0, 1.0 - (price / max_price))
        score = (RATING_WEIGHT * rating_norm) + (HIGH_RATED_WEIGHT * high_rated) + (PRICE_WEIGHT * price_norm)

        scored.append({**item, "_score": score})

    ranked = sorted(scored, key=lambda x: x["_score"], reverse=True)
    for r in ranked:
        del r["_score"]

    logger.info("Ranked %d recommendations deterministically", len(ranked))
    return ranked
