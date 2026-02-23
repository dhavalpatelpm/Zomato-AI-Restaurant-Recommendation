"""
Phase 1 Data Acquisition: Schema and sanity validation for restaurant dataset.
"""

import logging

import pandas as pd

REQUIRED_COLUMNS = ["locality", "cuisines", "price_range", "rating", "restaurant_name"]


logger = logging.getLogger(__name__)


class DatasetValidationError(Exception):
    """Raised when dataset schema or sanity checks fail."""

    pass


def validate_dataset_schema(df: pd.DataFrame) -> None:
    """
    Validate that the dataset has required columns and passes basic sanity checks.

    Args:
        df: DataFrame to validate.

    Raises:
        DatasetValidationError: If required columns are missing or null checks fail.
    """
    if not isinstance(df, pd.DataFrame):
        raise DatasetValidationError(
            f"Expected pandas DataFrame, got {type(df).__name__}"
        )

    if df.empty:
        raise DatasetValidationError("Dataset is empty")

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise DatasetValidationError(
            f"Missing required columns: {missing}. "
            f"Required: {REQUIRED_COLUMNS}. Found: {list(df.columns)}"
        )

    for col in REQUIRED_COLUMNS:
        null_count = df[col].isna().sum()
        if null_count == len(df):
            raise DatasetValidationError(
                f"Column '{col}' is entirely null"
            )
        if null_count > 0:
            logger.warning(
                "Column '%s' has %d null values (%.1f%%)",
                col,
                null_count,
                100.0 * null_count / len(df),
            )

    logger.info(
        "Dataset validation passed: %d rows, %d columns",
        len(df),
        len(df.columns),
    )
