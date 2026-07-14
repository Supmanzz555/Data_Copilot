from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import APIRouter, Response

router = APIRouter()

REQUEST_COUNT = Counter("datacopilot_requests_total", "Total requests", ["tool"])
REQUEST_LATENCY = Histogram(
    "datacopilot_request_latency_seconds", "Request latency", ["tool"]
)
ACTIVE_REQUESTS = Gauge("datacopilot_active_requests", "Active requests")
ERROR_COUNT = Counter("datacopilot_errors_total", "Total errors", ["type"])


@router.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type="text/plain")
