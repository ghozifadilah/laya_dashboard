from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from app.schemas.predict import RoutingMetadata


class EmailStateRequest(BaseModel):
    subject: str = Field(..., description="Subject line of the email")
    body: str = Field(..., description="Raw text or HTML body of the email")
    sender: Optional[str] = Field(None, description="Sender email address or display name")
    clean: bool = Field(True, description="Whether to automatically strip signatures, replies, and excessive whitespace")
    extra: Optional[Dict[str, Any]] = Field(None, description="Optional extra metadata fields")


class EmailCleanRequest(BaseModel):
    body: str = Field(..., description="Raw email text body containing signatures, quotes, or headers")
    max_chars: int = Field(3000, description="Maximum characters to retain after cleaning")


class EmailCleanResponse(BaseModel):
    cleaned_text: str = Field(..., description="Cleaned email body text")
    original_length: int = Field(..., description="Character count before cleaning")
    cleaned_length: int = Field(..., description="Character count after cleaning")
    compression_ratio: float = Field(..., description="Ratio of cleaned characters to original characters")


class EmailTriageRequest(BaseModel):
    subject: str = Field("", description="Email subject")
    body: str = Field(..., description="Email body content")
    sender: Optional[str] = Field(None, description="Sender email address")
    categories: Optional[Dict[str, str]] = Field(
        None,
        description="Custom email classification categories (e.g. {'billing': '...', 'security': '...'}).",
    )
    clean: bool = Field(True, description="Whether to clean the email body first")
    model: Optional[str] = Field(None, description="Optional model checkpoint override")


class EmailTriageResponse(BaseModel):
    success: bool = Field(True, description="Triage execution status")
    clean_state: Dict[str, Any] = Field(..., description="Structured email state after cleaning and normalization")
    answers: Dict[str, Any] = Field(..., description="Full model predictions for email questions")
    summary: Dict[str, Any] = Field(..., description="Key triage summary fields (category, urgency, churn_risk, etc.)")
    routing: Optional[RoutingMetadata] = Field(None, description="Routing decision")
    latency_ms: float = Field(..., description="Inference latency in milliseconds")
