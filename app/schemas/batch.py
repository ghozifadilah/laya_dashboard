from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from app.schemas.predict import PredictRequest, PredictResponse, QuestionSchema


class BatchPredictRequest(BaseModel):
    items: Optional[List[Union[str, Dict[str, Any], List[Any]]]] = Field(
        None,
        description="List of states/inputs to evaluate when sharing the same questions across all items.",
    )
    questions: Optional[Dict[str, Union[QuestionSchema, Dict[str, Any]]]] = Field(
        None,
        description="Shared question schema to apply to all items in `items`.",
    )
    preset: Optional[str] = Field(
        None,
        description="Preset name to apply to all items in `items`.",
    )
    requests: Optional[List[PredictRequest]] = Field(
        None,
        description="Alternative heterogeneous list of individual PredictRequest objects with distinct questions/presets per item.",
    )
    model: Optional[str] = Field(
        None,
        description="Optional model override applied to all items in the batch.",
    )


class BatchPredictResponse(BaseModel):
    success: bool = Field(True, description="Batch status")
    results: List[PredictResponse] = Field(..., description="List of prediction responses corresponding to each input item")
    total_items: int = Field(..., description="Total count of evaluated items")
    total_latency_ms: float = Field(..., description="Total processing time for the batch in milliseconds")
    average_latency_ms: float = Field(..., description="Average processing time per item in milliseconds")
