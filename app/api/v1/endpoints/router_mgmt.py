from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_api_key
from app.schemas.models import (
    InspectRouteRequest,
    InspectRouteResponse,
    PreloadRequest,
    PreloadResponse,
    UnloadResponse,
)
from app.services.laya_engine import get_laya_engine, LayaEngine

router = APIRouter()


@router.post(
    "/router/preload",
    response_model=PreloadResponse,
    summary="Preload model checkpoints into resident memory/VRAM",
    description="Loads specified checkpoints (e.g. ['english', 'multilingual']) into memory to achieve instant sub-35ms response time.",
)
async def preload_models(
    request: PreloadRequest,
    api_key: str = Depends(get_api_key),
    engine: LayaEngine = Depends(get_laya_engine),
) -> PreloadResponse:
    try:
        loaded = engine.preload(request.models)
        return PreloadResponse(
            success=True,
            message=f"Preloaded checkpoints successfully: {loaded}",
            loaded_models=loaded,
            device=engine.device,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Preload failed: {str(e)}")


@router.post(
    "/router/unload",
    response_model=UnloadResponse,
    summary="Unload resident models to free memory",
    description="Evicts loaded models from RAM/VRAM.",
)
async def unload_models(
    api_key: str = Depends(get_api_key),
    engine: LayaEngine = Depends(get_laya_engine),
) -> UnloadResponse:
    try:
        loaded = engine.unload()
        return UnloadResponse(
            success=True,
            message="Resident models unloaded successfully.",
            loaded_models=loaded,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unload failed: {str(e)}")


@router.post(
    "/router/inspect",
    response_model=InspectRouteResponse,
    summary="Inspect routing decision without running model forward pass (<0.5ms)",
    description="Determines which checkpoint the Router will select for a given state/questions and explains why.",
)
async def inspect_route(
    request: InspectRouteRequest,
    engine: LayaEngine = Depends(get_laya_engine),
) -> InspectRouteResponse:
    try:
        dec = engine.inspect_route(
            state=request.state,
            questions=request.questions,
            auto_task_detection=request.auto_task_detection,
        )
        return InspectRouteResponse(**dec)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
