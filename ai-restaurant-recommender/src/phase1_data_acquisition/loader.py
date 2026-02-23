"""
Phase 1 Data Acquisition: Dataset loader for Hugging Face Zomato restaurant dataset.
"""

import logging
from pathlib import Path
from typing import Optional, Union

import pandas as pd
from datasets import load_dataset

from .validator import validate_dataset_schema

REQUIRED_COLUMNS = ["locality", "cuisines", "price_range", "rating", "restaurant_name"]
DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"
COLUMN_MAPPING = {
    "restaurant_name": ["name", "restaurant_name", "restaurant name", "Restaurant_Name"],
    "locality": ["location", "locality", "Locality"],
    "cuisines": ["cuisines", "Cuisines"],
    "price_range": ["approx_cost(for two people)", "price_range", "price range", "Price_range"],
    "rating": ["rate", "rating", "Rating", "aggregate_rating", "Aggregate_rating"],
}


logger = logging.getLogger(__name__)


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map dataset columns to required schema if names differ."""
    normalized = df.copy()
    current_cols = {c.lower().replace(" ", "_").replace("(", "").replace(")", ""): c for c in df.columns}
    rename_map = {}

    for target, candidates in COLUMN_MAPPING.items():
        for cand in candidates:
            cand_normalized = cand.lower().replace(" ", "_").replace("(", "").replace(")", "")
            if cand_normalized in current_cols:
                orig = current_cols[cand_normalized]
                if orig != target:
                    rename_map[orig] = target
                break

    if rename_map:
        normalized = normalized.rename(columns=rename_map)
    return normalized


def load_dataset_from_hf(
    dataset_id: str = DATASET_ID,
    raw_dir: Optional[Union[Path, str]] = None,
    split: str = "train",
) -> pd.DataFrame:
    """
    Download the Zomato restaurant dataset from Hugging Face and load as a pandas DataFrame.

    Args:
        dataset_id: Hugging Face dataset identifier.
        raw_dir: Directory to save raw data copy. Defaults to data/raw relative to project root.
        split: Dataset split to load (e.g. 'train'). Defaults to 'train'.

    Returns:
        pandas DataFrame with restaurant data.

    Raises:
        ValueError: If dataset load fails or returned data is invalid.
    """
    logger.info("Loading dataset from Hugging Face: %s", dataset_id)
    project_root = Path(__file__).resolve().parents[2]
    cache_dir = project_root / ".cache" / "huggingface" / "datasets"
    cache_dir.mkdir(parents=True, exist_ok=True)
    dataset = load_dataset(dataset_id, cache_dir=str(cache_dir))

    if split not in dataset:
        available = list(dataset.keys())
        raise ValueError(
            f"Split '{split}' not found in dataset. Available splits: {available}"
        )

    hf_split = dataset[split]
    df = hf_split.to_pandas()

    df = _normalize_columns(df)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Dataset missing required columns after normalization: {missing}. "
            f"Available columns: {list(df.columns)}"
        )

    raw_path = raw_dir or Path(__file__).resolve().parents[2] / "data" / "raw"
    raw_path = Path(raw_path)
    raw_path.mkdir(parents=True, exist_ok=True)
    raw_file = raw_path / "zomato_restaurants_raw.parquet"
    df.to_parquet(raw_file, index=False)
    logger.info("Saved raw dataset to %s (%d rows)", raw_file, len(df))

    validate_dataset_schema(df)
    return df
