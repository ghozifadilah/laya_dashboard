from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_api_key
from app.schemas.batch import BatchPredictRequest, BatchPredictResponse
from app.services.laya_engine import get_laya_engine, LayaEngine

router = APIRouter()


@router.post(
    "/predict/batch",
    response_model=BatchPredictResponse,
    summary="Batch evaluate typed decisions over multiple states",
    description="Evaluates multiple state items with either a shared question schema or heterogeneous per-item requests.",
)
async def batch_predict_decision(
    request: BatchPredictRequest,
    api_key: str = Depends(get_api_key),
    engine: LayaEngine = Depends(get_laya_engine),
) -> BatchPredictResponse:
    try:
        # Convert questions if provided
        questions_dict = None
        if request.questions is not None:
            questions_dict = {}
            for q_id, q_val in request.questions.items():
                if hasattr(q_val, "model_dump"):
                    questions_dict[q_id] = q_val.model_dump()
                elif isinstance(q_val, dict):
                    questions_dict[q_id] = q_val

        result = engine.batch_predict(
            items=request.items,
            questions=questions_dict,
            preset=request.preset,
            requests=request.requests,
            model=request.model,
        )
        return BatchPredictResponse(**result)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Batch error: {str(e)}")
