import time
from typing import Any, Dict
from fastapi import APIRouter, Depends
import torch
from app.core.config import settings
from app.services.laya_engine import get_laya_engine, LayaEngine

router = APIRouter()
START_TIME = time.time()


@router.get(
    "/health",
    summary="General health and status check",
    tags=["Health"],
)
async def health_check(engine: LayaEngine = Depends(get_laya_engine)) -> Dict[str, Any]:
    status_info = engine.get_status()
    uptime_seconds = round(time.time() - START_TIME, 2)

    return {
        "status": "healthy",
        "version": settings.VERSION,
        "uptime_seconds": uptime_seconds,
        "device": status_info["device"],
        "cuda_available": status_info["cuda_available"],
        "loaded_models": status_info["loaded_models"],
        "mock_mode": settings.MOCK_MODE,
    }


@router.get(
    "/health/ready",
    summary="Readiness probe for load balancers and orchestrators",
    tags=["Health"],
)
async def readiness_probe(engine: LayaEngine = Depends(get_laya_engine)) -> Dict[str, Any]:
    return {"ready": True, "device": engine.device}


@router.get(
    "/health/live",
    summary="Liveness probe",
    tags=["Health"],
)
async def liveness_probe() -> Dict[str, Any]:
    return {"live": True}
