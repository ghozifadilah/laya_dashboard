from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


class QuestionSchema(BaseModel):
    type: Literal["choice", "score", "noul"] = Field(
        ...,
        description="Type of the question: 'choice' (categorical), 'score' (ordinal/scale), or 'noul' (binary boolean).",
    )
    instructions: str = Field(
        ...,
        description="Instruction/prompt prompt for the question. Can reference state fields.",
    )
    criteria: Optional[Union[Dict[str, Optional[str]], List[str], Dict[str, str]]] = Field(
        None,
        description=(
            "Criteria for options. For 'choice': dict of option -> description. "
            "For 'score': list of level descriptions in ascending order. "
            "For 'noul': optional dict with 'true' and 'false' descriptions."
        ),
    )


class RoutingMetadata(BaseModel):
    model: str = Field(..., description="Selected model checkpoint (e.g. 'english', 'multilingual', 'typed-decisions')")
    repo: Optional[str] = Field(None, description="HuggingFace model repository or checkpoint identifier")
    reason: str = Field(..., description="Reason for the routing decision")
    detected_language: Optional[str] = Field(None, description="Detected ISO language code (e.g. 'en', 'es', 'hi')")
    detected_script: Optional[str] = Field(None, description="Detected script (e.g. 'latin', 'devanagari', 'cyrillic', 'han')")
    script_profile: Optional[Dict[str, float]] = Field(None, description="Detailed character script distribution breakdown")


class AnswerItem(BaseModel):
    choice: Optional[Union[str, bool, int]] = Field(None, description="Predicted choice / boolean value / category")
    confidence: float = Field(..., description="Calibrated confidence score between 0.0 and 1.0")
    score: Optional[int] = Field(None, description="Predicted ordinal score (0-indexed) for score questions")
    level: Optional[str] = Field(None, description="Label/criterion corresponding to the predicted score level")
    probability: Optional[float] = Field(None, description="Calibrated probability for noul (true/false) questions")
    probs: Optional[Union[Dict[str, float], List[float]]] = Field(
        None, description="Full calibrated probability distribution across all options"
    )


class PredictRequest(BaseModel):
    state: Union[str, Dict[str, Any], List[Any]] = Field(
        ...,
        description="The context or input state to evaluate. Can be plain text or structured JSON (ticket, email, payload).",
        examples=[
            {
                "from": "user@acme.com",
                "subject": "Duplicate charge on invoice #4411",
                "body": "Hi, we were billed twice for March. Please refund the duplicate today or we will cancel our plan.",
            }
        ],
    )
    questions: Optional[Dict[str, Union[QuestionSchema, Dict[str, Any]]]] = Field(
        None,
        description="Dictionary of typed questions to evaluate in a single forward pass. If omitted, preset must be specified.",
    )
    preset: Optional[str] = Field(
        None,
        description="Name of a built-in preset to use: 'triage', 'email', 'guard', 'moderation', 'router', 'customer_service', 'agent_trace', 'invoice', 'security_incident'.",
    )
    model: Optional[str] = Field(
        None,
        description="Explicit checkpoint override ('english', 'multilingual', 'typed-decisions', or custom repo). If None, automatic routing is used.",
    )
    auto_task_detection: bool = Field(
        False,
        description="If True, automatically detect if questions match a typed-decisions workflow.",
    )
    max_len: Optional[int] = Field(
        None,
        description="Maximum sequence length for tokenization (defaults to model context length).",
    )


class PredictResponse(BaseModel):
    success: bool = Field(True, description="Indicates if the prediction completed successfully")
    answers: Dict[str, Any] = Field(..., description="Predictions for each question id")
    routing: Optional[RoutingMetadata] = Field(None, description="Routing and language detection metadata")
    latency_ms: float = Field(..., description="Inference execution latency in milliseconds")
