#!/usr/bin/env python3
"""
Get the top 5 cuisines in Bangalore from the Zomato dataset.
Run from ai-restaurant-recommender: python scripts/top_cuisines_bangalore.py
"""

import sys
from pathlib import Path

# Add project root so we can import from src
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import pandas as pd
from src.phase1_data_acquisition import load_dataset_from_hf
from src.phase2_data_processing import process_data


def get_top_cuisines(df: pd.DataFrame, top_n: int = 5) -> list[tuple[str, int]]:
    """Count cuisine occurrences and return top N by frequency."""
    counts: dict[str, int] = {}

    if "cuisines_list" in df.columns:
        for cuisines_list in df["cuisines_list"].dropna():
            if isinstance(cuisines_list, list):
                for c in cuisines_list:
                    if c and str(c).strip():
                        name = str(c).strip().lower()
                        counts[name] = counts.get(name, 0) + 1
            elif isinstance(cuisines_list, str):
                for c in cuisines_list.split(","):
                    if c.strip():
                        name = c.strip().lower()
                        counts[name] = counts.get(name, 0) + 1

    if "cuisines" in df.columns and not counts:
        for cuisines_str in df["cuisines"].dropna():
            for c in str(cuisines_str).split(","):
                if c.strip():
                    name = c.strip().lower()
                    counts[name] = counts.get(name, 0) + 1

    sorted_cuisines = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_cuisines[:top_n]


def main():
    print("Loading Bangalore Zomato dataset...")
    raw_df = load_dataset_from_hf()
    df = process_data(raw_df)
    print(f"Loaded {len(df)} restaurant records.\n")

    top5 = get_top_cuisines(df, top_n=5)
    print("Top 5 cuisines in Bangalore (by number of restaurants):\n")
    for i, (cuisine, count) in enumerate(top5, 1):
        print(f"  {i}. {cuisine.title():<25} ({count} restaurants)")


if __name__ == "__main__":
    main()
