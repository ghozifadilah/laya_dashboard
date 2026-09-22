from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from app.schemas.predict import RoutingMetadata


class ShortlistRequest(BaseModel):
    state: Union[str, Dict[str, Any], List[Any]] = Field(
        ...,
        description="The context or text state to evaluate against candidate options.",
    )
    instructions: str = Field(
        ...,
        description="Instructions / question prompt for selecting among options.",
        examples=["Which product category best matches the user inquiry?"],
    )
    criteria: Union[Dict[str, Optional[str]], List[str]] = Field(
        ...,
        description="List of candidate categories (or dict of category -> description) - can contain 50 to 500+ items.",
    )
    k: int = Field(
        20,
        description="Number of top candidates to shortlist in the first retrieval stage.",
        ge=2,
        le=100,
    )
    model: Optional[str] = Field(None, description="Optional model checkpoint override")


class CandidateItem(BaseModel):
    name: str = Field(..., description="Candidate option name")
    description: Optional[str] = Field(None, description="Description of the option if provided")


class ShortlistResponse(BaseModel):
    success: bool = Field(True, description="Shortlist execution status")
    selected_choice: str = Field(..., description="Final selected candidate option")
    confidence: float = Field(..., description="Confidence score for the winning candidate")
    shortlisted_candidates: List[str] = Field(..., description="Candidates filtered in the top-k stage")
    answers: Dict[str, Any] = Field(..., description="Detailed prediction result")
    routing: Optional[RoutingMetadata] = Field(None, description="Routing decision")
    latency_ms: float = Field(..., description="Total execution time in milliseconds")
