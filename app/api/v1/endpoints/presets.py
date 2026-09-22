from fastapi import APIRouter, Depends, HTTPException, Path, status
from app.core.security import get_api_key
from app.schemas.predict import PredictResponse
from app.schemas.presets import PresetDetail, PresetExecuteRequest, PresetListResponse
from app.services.laya_engine import get_laya_engine, LayaEngine
from app.services.presets_service import presets_catalog

router = APIRouter()


@router.get(
    "/presets",
    response_model=PresetListResponse,
    summary="List all ready-to-use question presets",
    description="Returns pre-configured question schemas for common decision workflows (triage, email, guard, moderation, customer_service, etc.).",
)
async def list_presets() -> PresetListResponse:
    presets = presets_catalog.list_presets()
    return PresetListResponse(
        total=len(presets),
        presets=[PresetDetail(**p) for p in presets],
    )


@router.get(
    "/presets/{preset_id}",
    response_model=PresetDetail,
    summary="Get details of a specific question preset",
)
async def get_preset_by_id(
    preset_id: str = Path(..., description="Preset identifier (e.g. 'triage', 'guard', 'email')"),
) -> PresetDetail:
    for p in presets_catalog.list_presets():
        if p["name"].lower() == preset_id.lower():
            return PresetDetail(**p)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Preset '{preset_id}' not found")


@router.post(
    "/presets/{preset_id}",
    response_model=PredictResponse,
    summary="Execute a preset directly over a given state",
)
async def execute_preset(
    preset_id: str = Path(..., description="Preset identifier"),
    request: PresetExecuteRequest = ...,
    api_key: str = Depends(get_api_key),
    engine: LayaEngine = Depends(get_laya_engine),
) -> PredictResponse:
    questions = presets_catalog.get_preset_questions(preset_id, custom_categories=request.categories)
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preset '{preset_id}' not found.",
        )

    try:
        result = engine.predict(
            state=request.state,
            questions=questions,
            model=request.model,
        )
        return PredictResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
