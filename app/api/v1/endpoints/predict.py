from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_api_key
from app.schemas.predict import PredictRequest, PredictResponse
from app.services.laya_engine import get_laya_engine, LayaEngine

router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictResponse,
    summary="Evaluate typed decisions over state (single forward pass)",
    description=(
        "Evaluates typed questions ('choice', 'score', 'noul') over any state "
        "(text, ticket, email, or JSON object) in a single fast forward pass (sub-35ms). "
        "Automatically routes between English and Multilingual (100+ languages) checkpoints."
    ),
)
@router.post(
    "/decide",
    response_model=PredictResponse,
    include_in_schema=False,
    summary="Alias for /predict",
)
async def predict_decision(
    request: PredictRequest,
    api_key: str = Depends(get_api_key),
    engine: LayaEngine = Depends(get_laya_engine),
) -> PredictResponse:
    try:
        # Convert Pydantic question models to raw dict if necessary
        questions_dict = None
        if request.questions is not None:
            questions_dict = {}
            for q_id, q_val in request.questions.items():
                if hasattr(q_val, "model_dump"):
                    questions_dict[q_id] = q_val.model_dump()
                elif isinstance(q_val, dict):
                    questions_dict[q_id] = q_val

        result = engine.predict(
            state=request.state,
            questions=questions_dict,
            preset=request.preset,
            model=request.model,
            auto_task_detection=request.auto_task_detection,
            max_len=request.max_len,
        )
        return PredictResponse(**result)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Inference error: {str(e)}")
