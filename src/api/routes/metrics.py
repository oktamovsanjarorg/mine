from fastapi import APIRouter, Response
try:
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

router = APIRouter(tags=["Metrics"])

@router.get("/metrics")
async def get_metrics():
    """Export Prometheus metrics."""
    if not HAS_PROMETHEUS:
        return Response(content="Prometheus metrics not available", media_type="text/plain", status_code=501)
    
    metrics_data = generate_latest()
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)
