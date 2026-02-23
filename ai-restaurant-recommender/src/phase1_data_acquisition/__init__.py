"""
Phase 1: Data Acquisition module for AI Restaurant Recommendation Service.

Provides dataset loading from Hugging Face and schema validation.
"""

from .loader import load_dataset_from_hf
from .validator import validate_dataset_schema

__all__ = ["load_dataset_from_hf", "validate_dataset_schema"]
