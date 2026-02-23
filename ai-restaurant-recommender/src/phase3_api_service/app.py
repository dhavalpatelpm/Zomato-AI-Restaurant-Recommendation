"""
Phase 3 API Service: FastAPI application entry point.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_groq_api_key
from .routes import router

try:
    from observability.logging_config import setup_logging
    from observability.middleware import RequestLoggingMiddleware
    from observability.metrics import get_metrics_response
    from observability.health import router as health_router
    OBSERVABILITY_AVAILABLE = True
except ImportError:
    OBSERVABILITY_AVAILABLE = False


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

if OBSERVABILITY_AVAILABLE:
    setup_logging()

app = FastAPI(
    title="AI Restaurant Recommendation Service",
    description="Backend API for restaurant recommendations",
    version="0.3.0",
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if OBSERVABILITY_AVAILABLE:
    app.add_middleware(RequestLoggingMiddleware)
    app.include_router(health_router)

    @app.get("/metrics")
    def metrics():
        return get_metrics_response()

app.include_router(router)


@app.on_event("startup")
def startup_validate_config() -> None:
    """Validate required configuration on startup."""
    get_groq_api_key()
    logger.info("Configuration validated successfully")
    # Pre-load dataset on startup for faster API responses
    try:
        from .service import _load_processed_dataset
        logger.info("Pre-loading dataset on startup...")
        df = _load_processed_dataset()
        logger.info("Dataset pre-loaded: %d rows ready", len(df))
    except Exception as e:
        logger.warning("Failed to pre-load dataset on startup: %s", str(e))


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint for readiness probes."""
    return {"status": "healthy", "service": "ai-restaurant-recommender"}
