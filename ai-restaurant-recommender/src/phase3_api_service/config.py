"""
Phase 3 API Service: Configuration and environment variables.
"""

import logging
import os

from dotenv import load_dotenv


load_dotenv()

logger = logging.getLogger(__name__)


def get_groq_api_key() -> str:
    """
    Load and validate GROQ_API_KEY from environment.

    Returns:
        GROQ API key string.

    Raises:
        ValueError: If GROQ_API_KEY is missing or empty.
    """
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        raise ValueError(
            "GROQ_API_KEY is required but not set. "
            "Add GROQ_API_KEY to .env or environment."
        )
    return key


def get_config() -> dict:
    """Load validated configuration."""
    return {"groq_api_key": get_groq_api_key()}
