"""
Tests for Phase 1: Data Acquisition.
"""

import logging

import pandas as pd
import pytest

from src.phase1_data_acquisition import load_dataset_from_hf, validate_dataset_schema
from src.phase1_data_acquisition.validator import DatasetValidationError


logging.basicConfig(level=logging.INFO)


def test_dataset_loads_successfully():
    """Test that the dataset loads from Hugging Face without raising."""
    df = load_dataset_from_hf()
    assert df is not None


def test_returned_object_is_pandas_dataframe():
    """Test that the loader returns a pandas DataFrame."""
    df = load_dataset_from_hf()
    assert isinstance(df, pd.DataFrame)


def test_required_columns_exist():
    """Test that all required columns are present in the dataset."""
    required = ["locality", "cuisines", "price_range", "rating", "restaurant_name"]
    df = load_dataset_from_hf()
    for col in required:
        assert col in df.columns, f"Missing column: {col}"


def test_no_crash_during_validation():
    """Test that validation runs without raising."""
    df = load_dataset_from_hf()
    validate_dataset_schema(df)


def test_dataset_is_not_empty():
    """Test that the loaded dataset contains at least one row."""
    df = load_dataset_from_hf()
    assert len(df) > 0
