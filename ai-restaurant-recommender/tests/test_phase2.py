"""
Tests for Phase 2: Data Processing & Feature Engineering.
Uses synthetic sample DataFrames only. No Hugging Face calls.
"""

import pandas as pd
import pytest

from src.phase2_data_processing import (
    clean_dataset,
    normalize_columns,
    create_features,
    process_data,
)


def _sample_df() -> pd.DataFrame:
    """Create synthetic sample DataFrame matching Phase 1 output schema."""
    return pd.DataFrame({
        "restaurant_name": ["Cafe A", "Cafe B", "Cafe C", "Cafe A", "Cafe D"],
        "locality": ["koramangala", "indiranagar", "whitefield", "koramangala", "hsr"],
        "cuisines": ["North Indian, Chinese", "Italian", "South Indian", "North Indian, Chinese", "Bakery"],
        "price_range": [300, "500", "800-1000", 300, 250],
        "rating": ["4.1/5", 4.5, "3.8", "4.2/5", 4.0],
        "votes": [100, 200, 50, 100, 75],
    })


def test_clean_function_removes_duplicates():
    """Clean function removes duplicate (restaurant_name, locality) pairs."""
    df = _sample_df()
    cleaned = clean_dataset(df)
    assert len(cleaned) == 4
    dup_pairs = cleaned.groupby(["restaurant_name", "locality"]).size()
    assert (dup_pairs <= 1).all()


def test_null_restaurant_name_rows_are_removed():
    """Rows with null restaurant_name are removed."""
    df = pd.DataFrame({
        "restaurant_name": ["A", None, "C"],
        "locality": ["x", "y", "z"],
        "cuisines": ["a", "b", "c"],
        "price_range": [100, 200, 300],
        "rating": [4.0, 4.0, 4.0],
    })
    cleaned = clean_dataset(df)
    assert len(cleaned) == 2
    assert cleaned["restaurant_name"].notna().all()


def test_rating_column_converted_to_float():
    """Rating column is converted to float after normalization."""
    df = pd.DataFrame({
        "restaurant_name": ["A"],
        "locality": ["x"],
        "cuisines": ["a"],
        "price_range": [100],
        "rating": ["4.1/5"],
    })
    normalized = normalize_columns(clean_dataset(df))
    assert normalized["rating"].dtype == float
    assert normalized["rating"].iloc[0] == pytest.approx(4.1)


def test_cuisines_list_column_exists_and_is_list():
    """cuisines_list column exists and contains lists."""
    df = pd.DataFrame({
        "restaurant_name": ["A"],
        "locality": ["x"],
        "cuisines": ["North Indian, Chinese"],
        "price_range": [100],
        "rating": [4.0],
    })
    normalized = normalize_columns(clean_dataset(df))
    assert "cuisines_list" in normalized.columns
    assert isinstance(normalized["cuisines_list"].iloc[0], list)
    assert normalized["cuisines_list"].iloc[0] == ["north indian", "chinese"]


def test_price_bucket_created():
    """price_bucket column is created with low/medium/high labels."""
    df = pd.DataFrame({
        "restaurant_name": ["A", "B", "C"],
        "locality": ["x", "y", "z"],
        "cuisines": ["a", "b", "c"],
        "price_range": [200, 500, 900],
        "rating": [4.0, 4.0, 4.0],
    })
    cleaned = clean_dataset(df)
    normalized = normalize_columns(cleaned)
    featured = create_features(normalized)
    assert "price_bucket" in featured.columns
    buckets = featured["price_bucket"].tolist()
    assert "low" in buckets
    assert "medium" in buckets
    assert "high" in buckets


def test_high_rated_flag_works_correctly():
    """high_rated_flag is True for rating >= 4.0."""
    df = pd.DataFrame({
        "restaurant_name": ["A", "B", "C"],
        "locality": ["x", "y", "z"],
        "cuisines": ["a", "b", "c"],
        "price_range": [100, 200, 300],
        "rating": [3.5, 4.0, 4.5],
    })
    cleaned = clean_dataset(df)
    normalized = normalize_columns(cleaned)
    featured = create_features(normalized)
    assert "high_rated_flag" in featured.columns
    flags = featured["high_rated_flag"].tolist()
    assert flags == [False, True, True]


def test_pipeline_returns_non_empty_dataframe():
    """Full pipeline returns non-empty DataFrame."""
    df = _sample_df()
    result = process_data(df)
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0


def test_no_unexpected_column_deletion():
    """Pipeline preserves expected columns and adds new ones."""
    df = _sample_df()
    original_cols = set(df.columns)
    result = process_data(df)
    for col in ["restaurant_name", "locality", "cuisines", "price_range", "rating"]:
        assert col in result.columns
    added = {"cuisines_raw", "cuisines_list", "cuisine_count", "high_rated_flag", "price_bucket", "rating_weighted_score"}
    for col in added:
        assert col in result.columns
