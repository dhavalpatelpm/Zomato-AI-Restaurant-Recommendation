"""
Phase 3 API Service: API route handlers.
"""

import logging
from datetime import datetime

from fastapi import APIRouter

from .schemas import RecommendationRequest, RecommendationResponse
from .service import filter_restaurants_with_fallback, _row_to_dict, get_all_localities, get_all_cuisines


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["recommendations"])


def _price_range_label(price_range: int) -> str:
    """Map numeric price range to human-readable label."""
    if price_range <= 500:
        return "budget"
    if price_range <= 1500:
        return "mid-range"
    return "premium"


def _build_reason(restaurant_name: str, rating: float, price_range: int, cuisines: str, user_cuisines: list) -> str:
    """Build a detailed 'Why you'll like it' reason for a restaurant."""
    price_label = _price_range_label(price_range)
    user_cuisines_str = ", ".join(user_cuisines[:3]) if user_cuisines else "diverse cuisines"
    # Use first cuisine from restaurant for "including X" to match user preference
    include_cuisine = user_cuisines[0] if user_cuisines else (cuisines.split(",")[0].strip() if cuisines else "diverse dishes")
    return (
        f"{restaurant_name} is a great match for someone looking for {user_cuisines_str} in the {price_label} price range "
        f"as it serves a diverse range of dishes, including {include_cuisine}, and has an excellent rating of {rating}. "
        f"With a cost of ₹{price_range} for two, it falls within the {price_label} price range, offering a high-quality dining experience."
    )


def _fallback_response(filtered, relaxed_message=None, user_cuisines=None):
    """Build fallback response when LLM is skipped or fails."""
    restaurants = [_row_to_dict(row) for _, row in filtered.iterrows()]
    cuisines_list = user_cuisines or []
    recs = []
    for r in restaurants:
        reason = _build_reason(
            r["restaurant_name"],
            r["rating"],
            r["price_range"],
            r.get("cuisines", ""),
            cuisines_list,
        )
        recs.append({
            "restaurant_name": r["restaurant_name"],
            "rating": r["rating"],
            "price_range": r["price_range"],
            "reason": reason,
            "confidence_score": 0.5,
            "locality": r.get("locality", ""),
            "address": r.get("address", r.get("locality", "")),
            "cuisines": r.get("cuisines", ""),
        })
    return RecommendationResponse(
        recommendations=recs,
        total_results=len(recs),
        generated_at=datetime.utcnow(),
        relaxed_message=relaxed_message,
    )


@router.post("/recommend", response_model=RecommendationResponse)
def recommend(request: RecommendationRequest) -> RecommendationResponse:
    """
    Get restaurant recommendations based on user preferences.

    Pipeline: Phase 1+2 (filter) -> Phase 4 (LLM) -> Phase 5 (format).
    Falls back to filtered-only when LLM fails or no results.
    """
    logger.info(
        "Recommendation request: locality=%s, price_range=%s, min_rating=%s, cuisines_count=%d",
        request.locality,
        request.price_range,
        request.min_rating,
        len(request.cuisines),
    )

    filtered, relaxed_message = filter_restaurants_with_fallback(
        locality=request.locality,
        price_range=request.price_range,
        min_rating=request.min_rating,
        cuisines=request.cuisines,
    )

    if filtered.empty:
        return RecommendationResponse(
            recommendations=[],
            total_results=0,
            generated_at=datetime.utcnow(),
        )

    try:
        from src.phase4_llm_engine import generate_recommendations
        from src.phase5_response_layer import build_final_response

        user_prefs = {
            "locality": request.locality,
            "price_range": request.price_range,
            "min_rating": request.min_rating,
            "cuisines": request.cuisines,
        }
        filtered_list = [_row_to_dict(row) for _, row in filtered.iterrows()]
        llm_output = generate_recommendations(user_prefs, filtered_list)
        final = build_final_response(llm_output, filtered, request.cuisines)
        name_to_meta = {}
        for _, row in filtered.iterrows():
            key = str(row.get("restaurant_name", "")).strip().lower()
            if key and key not in name_to_meta:
                addr = str(row.get("address", "")).strip() if "address" in row.index else ""
                name_to_meta[key] = {
                    "locality": str(row.get("locality", "")),
                    "address": addr or str(row.get("locality", "")),
                    "cuisines": str(row.get("cuisines_raw", row.get("cuisines", ""))),
                }
        recs = []
        for r in final.recommendations:
            d = r.model_dump()
            key = str(r.restaurant_name).strip().lower()
            if key in name_to_meta:
                d.update(name_to_meta[key])
            recs.append(d)
        return RecommendationResponse(
            recommendations=recs,
            total_results=final.total_results,
            generated_at=final.generated_at,
            relaxed_message=relaxed_message,
        )
    except Exception as e:
        logger.warning("LLM pipeline failed, using fallback: %s", str(e))
        return _fallback_response(filtered, relaxed_message, request.cuisines)


@router.get("/localities")
def get_localities() -> dict:
    """Get all available localities from the dataset."""
    try:
        localities = get_all_localities()
        return {"localities": localities, "count": len(localities)}
    except Exception as e:
        logger.error("Error fetching localities: %s", str(e))
        return {"localities": [], "count": 0}


@router.get("/cuisines")
def get_cuisines() -> dict:
    """Get all available cuisines from the dataset."""
    try:
        cuisines = get_all_cuisines()
        return {"cuisines": cuisines, "count": len(cuisines)}
    except Exception as e:
        logger.error("Error fetching cuisines: %s", str(e))
        return {"cuisines": [], "count": 0}
