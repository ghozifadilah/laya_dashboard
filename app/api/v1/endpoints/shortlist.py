from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_api_key
from app.schemas.shortlist import ShortlistRequest, ShortlistResponse
from app.services.laya_engine import get_laya_engine, LayaEngine
from app.services.shortlist_service import shortlist_service

router = APIRouter()


@router.post(
    "/shortlist",
    response_model=ShortlistResponse,
    summary="Evaluate decision over large taxonomy option spaces (top-k shortlisting)",
    description=(
        "Handles categorization and choice questions over large option sets (50 to 500+ items). "
        "Shortlists top-k candidate choices before passing into Laya's single forward pass."
    ),
)
async def shortlist_decision(
    request: ShortlistRequest,
    api_key: str = Depends(get_api_key),
    engine: LayaEngine = Depends(get_laya_engine),
) -> ShortlistResponse:
    try:
        res = shortlist_service.execute_shortlist(
            engine=engine,
            state=request.state,
            instructions=request.instructions,
            criteria=request.criteria,
            k=request.k,
            model=request.model,
        )
        return ShortlistResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Shortlist error: {str(e)}")
