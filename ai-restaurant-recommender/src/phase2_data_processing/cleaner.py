"""
Phase 2 Data Processing: Dataset cleaning for restaurant recommendation.
"""

import logging
from typing import List

import pandas as pd


logger = logging.getLogger(__name__)

REQUIRED_STRING_COLUMNS = ["restaurant_name", "locality", "cuisines"]


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the restaurant dataset by removing invalid rows and normalizing strings.

    Drops duplicates, removes rows with null restaurant_name or locality,
    drops rows with null rating, and strips whitespace from string columns.

    Args:
        df: Raw DataFrame from Phase 1.

    Returns:
        Cleaned DataFrame.

    Raises:
        ValueError: If required columns are missing.
    """
    required = ["restaurant_name", "locality", "rating"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for cleaning: {missing}")

    initial_rows = len(df)
    cleaned = df.copy()

    cleaned = cleaned.drop_duplicates(subset=["restaurant_name", "locality"], keep="first")
    dup_removed = initial_rows - len(cleaned)
    if dup_removed > 0:
        logger.info("Removed %d duplicate rows (restaurant_name + locality)", dup_removed)

    before = len(cleaned)
    cleaned = cleaned.dropna(subset=["restaurant_name"])
    removed = before - len(cleaned)
    if removed > 0:
        logger.info("Removed %d rows with null restaurant_name", removed)

    before = len(cleaned)
    cleaned = cleaned.dropna(subset=["locality"])
    removed = before - len(cleaned)
    if removed > 0:
        logger.info("Removed %d rows with null locality", removed)

    before = len(cleaned)
    cleaned = cleaned.dropna(subset=["rating"])
    removed = before - len(cleaned)
    if removed > 0:
        logger.info("Removed %d rows with null rating", removed)

    string_columns = [
        c for c in REQUIRED_STRING_COLUMNS
        if c in cleaned.columns and cleaned[c].dtype == object
    ]
    for col in string_columns:
        cleaned[col] = cleaned[col].astype(str).str.strip()

    before = len(cleaned)
    cleaned = cleaned[cleaned["restaurant_name"] != ""]
    cleaned = cleaned[cleaned["locality"] != ""]
    removed = before - len(cleaned)
    if removed > 0:
        logger.info("Removed %d rows with empty restaurant_name or locality", removed)

    total_removed = initial_rows - len(cleaned)
    logger.info("Cleaning complete: %d rows removed, %d rows remaining", total_removed, len(cleaned))

    return cleaned.reset_index(drop=True)
