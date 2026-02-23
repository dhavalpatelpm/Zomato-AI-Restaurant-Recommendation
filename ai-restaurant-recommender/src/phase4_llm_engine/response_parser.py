"""
Phase 4 LLM Engine: Parse and validate LLM JSON response.
"""

import json
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

REQUIRED_KEYS = ["restaurant_name", "reason", "rating", "price_range"]


class LLMResponseParseError(Exception):
    """Raised when LLM response is malformed or invalid."""

    pass


def parse_llm_response(response_text: str) -> Dict[str, Any]:
    """
    Parse and validate LLM JSON response.

    Args:
        response_text: Raw text from Groq LLM.

    Returns:
        Structured dict with 'recommendations' list.

    Raises:
        LLMResponseParseError: If JSON is invalid or structure is wrong.
    """
    if not response_text or not response_text.strip():
        raise LLMResponseParseError("Response text is empty")

    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as e:
        raise LLMResponseParseError(f"Invalid JSON: {e}") from e

    if not isinstance(data, dict):
        raise LLMResponseParseError("Response is not a JSON object")

    if "recommendations" not in data:
        raise LLMResponseParseError("Missing required key: recommendations")

    recs = data["recommendations"]
    if not isinstance(recs, list):
        raise LLMResponseParseError("recommendations must be a list")

    for i, item in enumerate(recs):
        if not isinstance(item, dict):
            raise LLMResponseParseError(
                f"recommendation[{i}] is not an object"
            )
        for key in REQUIRED_KEYS:
            if key not in item:
                raise LLMResponseParseError(
                    f"recommendation[{i}] missing required key: {key}"
                )

    logger.info("Parsed %d recommendations from LLM response", len(recs))
    return data
