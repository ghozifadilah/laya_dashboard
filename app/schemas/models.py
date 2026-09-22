from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    name: str = Field(..., description="Canonical model identifier: 'english', 'multilingual', 'typed-decisions'")
    repo: str = Field(..., description="Hugging Face hub repo and subfolder")
    encoder: str = Field(..., description="Underlying transformer encoder backbone")
    params: str = Field(..., description="Parameter count")
    context_tokens: int = Field(..., description="Maximum context window tokens")
    use_case: str = Field(..., description="Primary use case / recommended tasks")
    is_loaded: bool = Field(..., description="True if currently cached/hot in memory/VRAM")


class ModelListResponse(BaseModel):
    device: str = Field(..., description="Hardware device currently active (e.g. 'cuda:0', 'cpu', 'mps')")
    cuda_available: bool = Field(..., description="Whether CUDA GPU acceleration is available")
    max_loaded: int = Field(..., description="Maximum concurrently loaded models in memory (LRU cache)")
    loaded_count: int = Field(..., description="Number of models currently hot in memory")
    models: List[ModelInfo] = Field(..., description="List of registered model checkpoints")


class PreloadRequest(BaseModel):
    models: Optional[List[str]] = Field(
        None,
        description="List of model names to preload (e.g. ['english', 'multilingual']). If None, all default models are preloaded.",
    )


class PreloadResponse(BaseModel):
    success: bool = Field(True, description="Preload operation status")
    message: str = Field(..., description="Summary of preloaded models")
    loaded_models: List[str] = Field(..., description="List of currently loaded models in memory")
    device: str = Field(..., description="Target device for preloaded checkpoints")


class UnloadResponse(BaseModel):
    success: bool = Field(True, description="Unload status")
    message: str = Field(..., description="Memory freed successfully")
    loaded_models: List[str] = Field(..., description="Remaining loaded models")


class InspectRouteRequest(BaseModel):
    state: Union[str, Dict[str, Any], List[Any]] = Field(
        ...,
        description="The context or text state to inspect for routing.",
    )
    questions: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional question schema to inspect alongside the state.",
    )
    auto_task_detection: bool = Field(
        False,
        description="Whether to check for typed-decisions workflow signatures.",
    )


class InspectRouteResponse(BaseModel):
    model: str = Field(..., description="The model checkpoint that Router will choose")
    reason: str = Field(..., description="Explanation of why this model was chosen")
    repo: Optional[str] = Field(None, description="Hugging Face repo or subfolder path")
    detected_language: Optional[str] = Field(None, description="Language code")
    detected_script: Optional[str] = Field(None, description="Detected script")
    script_profile: Optional[Dict[str, float]] = Field(None, description="Script percentage breakdown")
