"""
Phase 2 Data Processing: Feature engineering for ranking and filtering.
"""

import logging
import math
from typing import Optional

import pandas as pd


logger = logging.getLogger(__name__)

PRICE_LOW_THRESHOLD = 400
PRICE_HIGH_THRESHOLD = 800
HIGH_RATED_THRESHOLD = 4.0


def create_features(
    df: pd.DataFrame,
    price_low: int = PRICE_LOW_THRESHOLD,
    price_high: int = PRICE_HIGH_THRESHOLD,
    high_rated_threshold: float = HIGH_RATED_THRESHOLD,
) -> pd.DataFrame:
    """
    Create feature columns for LLM ranking and filtering.

    Adds cuisine_count, high_rated_flag, price_bucket, and optionally
    rating_weighted_score when review_count or votes column exists.

    Args:
        df: Transformed DataFrame from transformer.
        price_low: Upper bound (exclusive) for low price bucket.
        price_high: Upper bound (exclusive) for medium price bucket.
        high_rated_threshold: Minimum rating for high_rated_flag.

    Returns:
        DataFrame with additional feature columns.
    """
    featured = df.copy()

    if "cuisines_list" in featured.columns:
        featured["cuisine_count"] = featured["cuisines_list"].apply(
            lambda x: len(x) if isinstance(x, list) else 0
        )
    else:
        featured["cuisine_count"] = 0

    if "rating" in featured.columns:
        featured["high_rated_flag"] = featured["rating"] >= high_rated_threshold
    else:
        featured["high_rated_flag"] = False

    if "price_range" in featured.columns:
        def _bucket(p: int) -> str:
            if p <= 0:
                return "unknown"
            if p < price_low:
                return "low"
            if p < price_high:
                return "medium"
            return "high"

        featured["price_bucket"] = featured["price_range"].apply(_bucket)
    else:
        featured["price_bucket"] = "unknown"

    review_col: Optional[str] = None
    for col in ["votes", "review_count", "reviews_count"]:
        if col in featured.columns:
            review_col = col
            break

    if review_col and "rating" in featured.columns:
        featured["rating_weighted_score"] = featured.apply(
            lambda row: row["rating"] * math.log(
                (int(row[review_col]) if pd.notna(row[review_col]) else 0) + 1
            ),
            axis=1,
        )
        logger.info("Created rating_weighted_score using column: %s", review_col)
    else:
        featured["rating_weighted_score"] = featured["rating"].fillna(0) if "rating" in featured.columns else 0.0

    logger.info(
        "Feature engineering complete: added cuisine_count, high_rated_flag, price_bucket, rating_weighted_score"
    )
    return featured
