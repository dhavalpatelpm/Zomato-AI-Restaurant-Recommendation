"""
Phase 3 API Service: Pydantic request and response schemas.
"""

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    """User preferences for restaurant recommendations."""

    locality: str = Field(..., min_length=1, description="Locality or area name")
    price_range: int = Field(..., ge=1, description="Maximum budget for two people")
    min_rating: float = Field(..., ge=0.0, le=5.0, description="Minimum rating filter")
    cuisines: List[str] = Field(default_factory=list, description="Preferred cuisines")


class RecommendationResponse(BaseModel):
    """Structured recommendation response (Phase 5 format with fallback)."""

    recommendations: List[dict] = Field(default_factory=list, description="Ranked recommendations")
    total_results: int = Field(..., ge=0, description="Number of results returned")
    generated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    relaxed_message: Optional[str] = Field(default=None, description="Message when filters were relaxed to find results")
