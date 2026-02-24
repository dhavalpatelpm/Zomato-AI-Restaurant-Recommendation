"""
Phase 3 API Service: Restaurant filtering and LLM context preparation.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


logger = logging.getLogger(__name__)

_processed_df: Optional[pd.DataFrame] = None
_MAX_RESULTS = 10


def _load_processed_dataset() -> pd.DataFrame:
    """Load and cache processed dataset from Phase 1 + Phase 2."""
    global _processed_df
    if _processed_df is not None:
        return _processed_df
    from src.phase1_data_acquisition import load_dataset_from_hf
    from src.phase2_data_processing import process_data

    logger.info("Loading and processing dataset (Phase 1 + Phase 2)")
    raw_df = load_dataset_from_hf()
    _processed_df = process_data(raw_df)
    logger.info("Dataset loaded: %d rows", len(_processed_df))
    return _processed_df


def filter_restaurants(
    locality: str,
    price_range: int,
    min_rating: float,
    cuisines: List[str],
) -> pd.DataFrame:
    """
    Filter restaurants by user preferences.

    Args:
        locality: Locality name (case insensitive).
        price_range: Maximum budget for two people (restaurants with price_range <= this).
        min_rating: Minimum rating threshold.
        cuisines: List of preferred cuisines (restaurant must have at least one).

    Returns:
        Filtered DataFrame sorted by rating descending, top _MAX_RESULTS.
    """
    df = _load_processed_dataset()
    filtered = df.copy()

    filtered = filtered[filtered["locality"].str.lower() == locality.strip().lower()]
    if len(filtered) == 0:
        logger.info("No matches for locality: %s", locality)
        return filtered

    filtered = filtered[filtered["price_range"] <= price_range]
    if len(filtered) == 0:
        logger.info("No matches for price_range <= %s", price_range)
        return filtered

    filtered = filtered[filtered["rating"] >= min_rating]
    if len(filtered) == 0:
        logger.info("No matches for min_rating >= %s", min_rating)
        return filtered

    if cuisines and "cuisines_list" in filtered.columns:
        cuisines_lower = [c.strip().lower() for c in cuisines if c.strip()]
        if cuisines_lower:
            def has_cuisine(row: Any) -> bool:
                lst = row if isinstance(row, list) else []
                return bool(set(cuisines_lower) & set(lst))

            filtered = filtered[filtered["cuisines_list"].apply(has_cuisine)]

    filtered = filtered.sort_values("rating", ascending=False).head(_MAX_RESULTS)
    logger.info("Filtered to %d results", len(filtered))
    return filtered


def filter_restaurants_with_fallback(
    locality: str,
    price_range: int,
    min_rating: float,
    cuisines: List[str],
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Filter restaurants; if no results, retry with relaxed criteria.
    Returns (filtered_df, relaxed_message or None).
    """
    filtered = filter_restaurants(locality, price_range, min_rating, cuisines)
    if not filtered.empty:
        return filtered, None

    # Relax: lower min_rating by 0.5 (down to 3.0 min)
    relaxed_rating = max(3.0, min_rating - 0.5)
    filtered = filter_restaurants(locality, price_range, relaxed_rating, cuisines)
    if not filtered.empty:
        logger.info("No results for strict filters; using relaxed min_rating=%.1f", relaxed_rating)
        return filtered, f"Showing top options (rating ≥ {relaxed_rating} — none matched rating ≥ {min_rating})"

    # Relax further: ignore cuisines
    filtered = filter_restaurants(locality, price_range, relaxed_rating, [])
    if not filtered.empty:
        logger.info("No results with cuisine match; showing top in locality")
        return filtered, f"Showing top-rated in {locality} (no exact cuisine match)"

    return filtered, None


def _row_to_dict(row: pd.Series) -> dict:
    """Convert DataFrame row to API response dict."""
    locality = str(row.get("locality", ""))
    address = str(row.get("address", "")).strip() if "address" in row.index else ""
    return {
        "restaurant_name": str(row.get("restaurant_name", "")),
        "locality": locality,
        "address": address or locality,
        "cuisines": str(row.get("cuisines_raw", row.get("cuisines", ""))),
        "price_range": int(row.get("price_range", 0)),
        "rating": float(row.get("rating", 0.0)),
    }


def get_all_localities() -> List[str]:
    """Get all unique localities from the dataset."""
    df = _load_processed_dataset()
    if "locality" not in df.columns:
        logger.warning("'locality' column not found in dataset")
        return []
    localities = df["locality"].dropna().unique().tolist()
    localities = [str(loc).strip().lower() for loc in localities if str(loc).strip()]
    localities = sorted(list(set([loc for loc in localities if loc])))
    logger.info("Found %d unique localities", len(localities))
    return localities


def get_restaurant_count() -> int:
    """Get total number of restaurants in the dataset."""
    df = _load_processed_dataset()
    return len(df)


def get_all_cuisines() -> List[str]:
    """Get all unique cuisines from the dataset."""
    df = _load_processed_dataset()
    cuisines_set = set()
    
    # Try cuisines_list first (processed list format)
    if "cuisines_list" in df.columns:
        for cuisines_list in df["cuisines_list"].dropna():
            if isinstance(cuisines_list, list):
                cuisines_set.update([c.strip().lower() for c in cuisines_list if c and str(c).strip()])
            elif isinstance(cuisines_list, str):
                # Handle string representation of list
                try:
                    import ast
                    parsed = ast.literal_eval(cuisines_list)
                    if isinstance(parsed, list):
                        cuisines_set.update([c.strip().lower() for c in parsed if c and str(c).strip()])
                except:
                    cuisines_set.update([c.strip().lower() for c in cuisines_list.split(",") if c.strip()])
    
    # Fallback to cuisines column (comma-separated string)
    if "cuisines" in df.columns:
        for cuisines_str in df["cuisines"].dropna():
            cuisines_set.update([c.strip().lower() for c in str(cuisines_str).split(",") if c.strip()])
    
    # Convert to title case and sort
    cuisines = sorted([c.title() for c in cuisines_set if c])
    logger.info("Found %d unique cuisines", len(cuisines))
    return cuisines


def prepare_llm_context(filtered_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Prepare context payload for Phase 4 (Groq LLM).

    Placeholder until Phase 4 integration. Returns structured context
    suitable for LLM prompt construction.

    Args:
        filtered_df: Filtered restaurant DataFrame.

    Returns:
        Dict with restaurants and metadata for LLM consumption.
    """
    restaurants = [_row_to_dict(row) for _, row in filtered_df.iterrows()]
    return {"restaurants": restaurants, "count": len(restaurants)}
