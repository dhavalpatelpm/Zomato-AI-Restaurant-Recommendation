"""
Phase 4 LLM Engine: Structured prompt construction for Groq.
"""

import json
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a restaurant recommendation expert.

Your task is to rank and recommend restaurants from the provided list based on user preferences.
Provide a brief, personalized reason for each recommendation.
Return ONLY valid JSON matching the specified format. No additional text."""

OUTPUT_FORMAT = """
{
  "recommendations": [
    {
      "restaurant_name": "",
      "reason": "",
      "rating": "",
      "price_range": ""
    }
  ]
}
"""


def build_recommendation_prompt(
    user_preferences: Dict[str, Any],
    filtered_restaurants: List[Dict[str, Any]],
) -> str:
    """
    Build structured prompt for Groq LLM.

    Args:
        user_preferences: Dict with locality, price_range, min_rating, cuisines.
        filtered_restaurants: List of restaurant dicts from Phase 3 filtering.

    Returns:
        Formatted user prompt string for LLM.
    """
    context_parts = [
        "## User Preferences",
        f"- Locality: {user_preferences.get('locality', 'N/A')}",
        f"- Max Budget (for two): {user_preferences.get('price_range', 'N/A')}",
        f"- Minimum Rating: {user_preferences.get('min_rating', 'N/A')}",
        f"- Preferred Cuisines: {user_preferences.get('cuisines', [])}",
        "",
        "## Filtered Restaurants (rank by relevance and quality)",
        json.dumps(filtered_restaurants[:10], indent=2),
        "",
        "## Instructions",
        "Rank these restaurants from best to worst match for the user. Provide a short reason for each.",
        "Output must be valid JSON in this exact format:",
        OUTPUT_FORMAT,
    ]

    user_prompt = "\n".join(context_parts)
    logger.info("Built recommendation prompt for %d restaurants", len(filtered_restaurants[:10]))
    return user_prompt
