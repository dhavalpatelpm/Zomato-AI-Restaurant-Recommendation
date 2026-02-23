"""
Phase 5 Response Layer: Confidence scoring for recommendations.
"""

import logging
from typing import Any, Dict, List, Optional

import pandas as pd


logger = logging.getLogger(__name__)

BASE_CONFIDENCE = 0.5
RATING_BOOST = 0.2
TOP_POSITION_BOOST = 0.15
IN_FILTERED_BOOST = 0.1
CUISINE_MATCH_BOOST = 0.05


def _normalize_name(name: str) -> str:
    return str(name).strip().lower()


def compute_confidence_score(
    recommendation: Dict[str, Any],
    filtered_df: pd.DataFrame,
    user_cuisines: Optional[List[str]] = None,
) -> float:
    """
    Compute confidence score for a single recommendation.

    Args:
        recommendation: Single recommendation dict.
        filtered_df: Filtered restaurants DataFrame.
        user_cuisines: Optional list of user's preferred cuisines for match boost.

    Returns:
        Confidence score between 0 and 1, rounded to 2 decimals.
    """
    score = BASE_CONFIDENCE

    rating_val = recommendation.get("rating") or recommendation.get("_rating")
    if rating_val is not None:
        try:
            r = float(rating_val)
            if r >= 4.5:
                score += RATING_BOOST
        except (TypeError, ValueError):
            pass

    name = _normalize_name(recommendation.get("restaurant_name", ""))
    if not name or filtered_df.empty:
        return round(min(1.0, max(0.0, score)), 2)

    df = filtered_df.copy()
    df["_name_norm"] = df["restaurant_name"].astype(str).str.strip().str.lower()
    matches = df[df["_name_norm"] == name]

    if not matches.empty:
        score += IN_FILTERED_BOOST
        idx = matches.index[0]
        position = df.index.get_loc(idx) if idx in df.index else 999
        if position < 3:
            score += TOP_POSITION_BOOST

        if user_cuisines and "cuisines_list" in df.columns:
            row = matches.iloc[0]
            rest_cuisines = row.get("cuisines_list", [])
            if isinstance(rest_cuisines, list):
                user_lower = [c.strip().lower() for c in user_cuisines if c]
                if set(user_lower) & set(rest_cuisines):
                    score += CUISINE_MATCH_BOOST

    return round(min(1.0, max(0.0, score)), 2)
