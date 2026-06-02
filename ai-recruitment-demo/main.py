# ddtrace must be imported before FastAPI so it can patch the ASGI framework.
# Traces are sent to a local Datadog agent (default: localhost:8126).
# Set DD_API_KEY, DD_SERVICE, DD_ENV in your .env (see .env.example).
import ddtrace.auto  # noqa: F401

from datetime import datetime

from fastapi import FastAPI

from routers.cv_router import router as cv_router
from routers.metrics_router import router as metrics_router
from routers.ranking_router import router as ranking_router
from routers.scoring_router import router as scoring_router
from services.metrics import count_cvs_processed, count_scoring_events

app = FastAPI(
    title="AI Recruitment Demo",
    description="AI-powered candidate scoring system for EU AI Act compliance demonstration.",
    version="0.1.0",
)

# ranking_router is registered first so its GET / is not shadowed
app.include_router(ranking_router)
app.include_router(cv_router)
app.include_router(scoring_router)
app.include_router(metrics_router)


@app.get("/health")
def health_check():
    """Return system health, current timestamp, and key event counts."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "cvs_processed": count_cvs_processed(),
        "scoring_events": count_scoring_events(),
    }
