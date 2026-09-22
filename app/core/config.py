import os
from typing import List, Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import torch


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "Laya Decision Engine API"
    PROJECT_DESCRIPTION: str = (
        "High-performance REST API backend for Laya — Multilingual, "
        "non-autoregressive System 1 decision engine with calibrated probabilities."
    )
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    WORKERS: int = 1

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Laya Engine Settings
    DEVICE: str = "auto"  # "auto", "cuda", "cpu", "mps"
    PRELOAD_ON_STARTUP: bool = True  # Preload models on server startup for instant sub-35ms latency
    PRELOAD_MODELS: List[str] = ["english", "multilingual"]
    MAX_LOADED_MODELS: int = 3  # Keep English, Multilingual, and Typed-Decisions simultaneously hot
    HF_TOKEN: Optional[str] = None
    DEFAULT_MAX_LEN: int = 512
    CHECKPOINTS_DIR: Optional[str] = None  # Optional custom local checkpoint path

    # Offline / Cache Mode: Avoid repeating HuggingFace online HEAD requests once files exist locally
    USE_LOCAL_CACHE_ONLY: bool = True

    # Mock mode for testing / environments without model downloads
    MOCK_MODE: bool = False

    # Security / API Key Authentication
    API_KEY_ENABLED: bool = False
    API_KEYS: List[str] = []

    @field_validator("API_KEYS", mode="before")
    @classmethod
    def assemble_api_keys(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        return []

    def get_resolved_device(self) -> str:
        """Resolve 'auto' to 'cuda' if torch.cuda.is_available() else 'cpu'."""
        if self.DEVICE == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return "mps"
            return "cpu"
        return self.DEVICE


settings = Settings()
