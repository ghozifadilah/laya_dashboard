from fastapi import APIRouter, Depends
from app.schemas.models import ModelInfo, ModelListResponse
from app.services.laya_engine import get_laya_engine, LayaEngine

router = APIRouter()


@router.get(
    "/models",
    response_model=ModelListResponse,
    summary="List available Laya checkpoints and device status",
    description="Returns registered model checkpoints, memory load status, context windows, and active hardware device (CUDA/CPU).",
)
async def list_models(engine: LayaEngine = Depends(get_laya_engine)) -> ModelListResponse:
    status_info = engine.get_status()
    models = [ModelInfo(**m) for m in status_info["models"]]
    return ModelListResponse(
        device=status_info["device"],
        cuda_available=status_info["cuda_available"],
        max_loaded=status_info["max_loaded"],
        loaded_count=status_info["loaded_count"],
        models=models,
    )
