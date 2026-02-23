"""
Phase 4 LLM Engine: End-to-end recommendation generation pipeline.
"""

import logging
from typing import Any, Dict, List

from .groq_client import call_groq_llm
from .prompt_builder import build_recommendation_prompt
from .response_parser import parse_llm_response


logger = logging.getLogger(__name__)


def generate_recommendations(
    user_preferences: Dict[str, Any],
    filtered_restaurants: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Generate ranked recommendations using Groq LLM.

    Pipeline: build prompt -> call Groq -> parse response -> return structured output.

    Args:
        user_preferences: Dict with locality, price_range, min_rating, cuisines.
        filtered_restaurants: List of restaurant dicts from Phase 3 filtering.

    Returns:
        Dict with 'recommendations' list, each item has restaurant_name, reason, rating, price_range.
    """
    logger.info("Starting LLM recommendation generation")

    prompt = build_recommendation_prompt(user_preferences, filtered_restaurants)
    logger.info("Prompt built, calling Groq LLM")

    raw_response = call_groq_llm(prompt)
    logger.info("Groq response received, parsing")

    parsed = parse_llm_response(raw_response)
    logger.info("LLM pipeline complete: %d recommendations", len(parsed.get("recommendations", [])))

    return parsed
