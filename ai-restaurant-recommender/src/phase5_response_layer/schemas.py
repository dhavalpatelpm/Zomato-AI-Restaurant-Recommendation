"""
Phase 5 Response Layer: Pydantic models for final API output.
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class RecommendationItem(BaseModel):
    """Single recommendation in final response."""

    restaurant_name: str = Field(..., min_length=1)
    rating: float = Field(..., ge=0.0, le=5.0)
    price_range: int = Field(..., ge=0)
    reason: str = Field(..., min_length=1)
    confidence_score: float = Field(..., ge=0.0, le=1.0)


class FinalResponse(BaseModel):
    """Production-ready API response schema."""

    recommendations: List[RecommendationItem] = Field(default_factory=list)
    total_results: int = Field(..., ge=0)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
