from fastapi import APIRouter, Depends
from app.schemas.lang import LangDetectRequest, LangDetectResponse
from app.services.laya_engine import get_laya_engine, LayaEngine

router = APIRouter()


@router.post(
    "/lang/detect",
    response_model=LangDetectResponse,
    summary="Detect language and script profile (<0.5ms)",
    description=(
        "Pure-Python script and language detector used by the Laya Router to inspect text "
        "and determine whether the request belongs to the English or Multilingual checkpoint."
    ),
)
async def detect_text_language(
    request: LangDetectRequest,
    engine: LayaEngine = Depends(get_laya_engine),
) -> LangDetectResponse:
    info = engine.detect_lang(request.text)
    return LangDetectResponse(**info)
