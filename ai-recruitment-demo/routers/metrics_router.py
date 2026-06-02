from fastapi import APIRouter

from services.metrics import get_metrics

router = APIRouter(tags=["Metrics"])


@router.get("/metrics")
def metrics():
    """Return aggregate system metrics: latency, override count, event totals."""
    return get_metrics()
