"""
Phase 5 Response Layer: End-to-end final response pipeline.
"""

import logging
from typing import Any, Dict, List, Optional

import pandas as pd

from .confidence import compute_confidence_score
from .formatter import format_final_response
from .ranker import apply_ranking
from .schemas import FinalResponse


logger = logging.getLogger(__name__)


def build_final_response(
    llm_output: Dict[str, Any],
    filtered_df: pd.DataFrame,
    user_cuisines: Optional[List[str]] = None,
) -> FinalResponse:
    """
    Build production-ready final response from LLM output.

    Pipeline: rank -> compute confidence -> format -> return schema.

    Args:
        llm_output: Parsed LLM response from Phase 4.
        filtered_df: Filtered restaurants DataFrame from Phase 3.
        user_cuisines: Optional user cuisine preferences for confidence scoring.

    Returns:
        Validated FinalResponse Pydantic model.
    """
    logger.info("Building final response from LLM output")

    ranked = apply_ranking(llm_output, filtered_df)
    logger.info("Ranking complete: %d items", len(ranked))

    cuisines = user_cuisines or []
    for rec in ranked:
        rec["confidence_score"] = compute_confidence_score(
            rec, filtered_df, cuisines if cuisines else None
        )
    logger.info("Confidence scores computed")

    response = format_final_response(ranked)
    logger.info("Final response built: %d recommendations", response.total_results)

    return response
