"""
Phase 2 Data Processing: End-to-end processing pipeline.
"""

import logging

import pandas as pd

from .cleaner import clean_dataset
from .transformer import normalize_columns
from .feature_engineering import create_features


logger = logging.getLogger(__name__)


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run the full Phase 2 data processing pipeline.

    Executes cleaning, normalization, and feature engineering in sequence.
    Returns a filter-ready structured dataset for downstream phases.

    Args:
        df: Validated DataFrame from Phase 1 (load_dataset_from_hf output).

    Returns:
        Processed DataFrame with clean schema and feature columns.
    """
    logger.info("Starting Phase 2 data processing pipeline: input %d rows", len(df))

    cleaned = clean_dataset(df)
    logger.info("Stage 1 (clean) complete: %d rows", len(cleaned))

    normalized = normalize_columns(cleaned)
    logger.info("Stage 2 (normalize) complete: %d rows", len(normalized))

    featured = create_features(normalized)
    logger.info("Stage 3 (features) complete: %d rows", len(featured))

    logger.info("Phase 2 pipeline complete: output %d rows, %d columns", len(featured), len(featured.columns))
    return featured.reset_index(drop=True)
