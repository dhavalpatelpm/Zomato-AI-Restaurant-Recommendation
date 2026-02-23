"""
Phase 2 Data Processing: Column normalization and schema standardization.
"""

import logging
import re
from typing import Any, List

import pandas as pd


logger = logging.getLogger(__name__)


def _parse_rating(value: Any) -> float:
    """Extract numeric rating from string (e.g. '4.1/5') or return float."""
    if pd.isna(value):
        return float("nan")
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if not s or s.upper() in ("NEW", "NA", "-", ""):
        return float("nan")
    match = re.search(r"(\d+\.?\d*)", s)
    if match:
        return float(match.group(1))
    return float("nan")


def _parse_price(value: Any) -> int:
    """Extract integer price from string (e.g. '300', '300-400') or return int."""
    if pd.isna(value):
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    s = str(value).strip().replace(",", "")
    match = re.search(r"(\d+)", s)
    if match:
        return int(match.group(1))
    return 0


def _split_cuisines(value: Any) -> List[str]:
    """Split cuisine string by comma and return trimmed lowercase list."""
    if pd.isna(value):
        return []
    s = str(value).strip()
    if not s:
        return []
    return [c.strip().lower() for c in s.split(",") if c.strip()]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize columns to standard types and formats for filtering and ranking.

    Converts rating to float, price_range to integer, locality to lowercase,
    and creates cuisines_raw and cuisines_list from cuisines.

    Args:
        df: Cleaned DataFrame from cleaner.

    Returns:
        Transformed DataFrame with normalized columns.

    Raises:
        ValueError: If required columns are missing.
    """
    required = ["restaurant_name", "locality", "cuisines", "price_range", "rating"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for normalization: {missing}")

    transformed = df.copy()

    transformed["rating"] = transformed["rating"].apply(_parse_rating)
    rows_with_nan_rating = transformed["rating"].isna().sum()
    if rows_with_nan_rating > 0:
        transformed = transformed.dropna(subset=["rating"]).reset_index(drop=True)
        logger.info("Dropped %d rows with unparseable rating", rows_with_nan_rating)

    if "price_range" in transformed.columns:
        transformed["price_range"] = transformed["price_range"].apply(_parse_price)

    if "locality" in transformed.columns:
        transformed["locality"] = transformed["locality"].astype(str).str.strip().str.lower()

    if "cuisines" in transformed.columns:
        transformed["cuisines_raw"] = transformed["cuisines"].astype(str).str.strip()
        transformed["cuisines_list"] = transformed["cuisines"].apply(_split_cuisines)

    logger.info("Normalization complete: %d rows", len(transformed))
    return transformed
