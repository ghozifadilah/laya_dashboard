from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class PresetDetail(BaseModel):
    name: str = Field(..., description="Unique identifier for the preset")
    title: str = Field(..., description="Human-friendly title of the preset")
    description: str = Field(..., description="Description of the business workflow solved by this preset")
    questions: Dict[str, Any] = Field(..., description="Pre-configured question schema")
    example_state: Union[str, Dict[str, Any]] = Field(..., description="Example state to test this preset")


class PresetListResponse(BaseModel):
    total: int = Field(..., description="Number of available presets")
    presets: List[PresetDetail] = Field(..., description="List of presets")


class PresetExecuteRequest(BaseModel):
    state: Union[str, Dict[str, Any], List[Any]] = Field(
        ...,
        description="The state/payload to evaluate against the chosen preset.",
    )
    model: Optional[str] = Field(
        None,
        description="Optional model override ('english', 'multilingual', 'typed-decisions').",
    )
    categories: Optional[Dict[str, str]] = Field(
        None,
        description="Optional custom categories override (specifically for 'email' or customizable presets).",
    )
