from typing import List, Optional
from pydantic import BaseModel, Field


class ApiKeyCreateRequest(BaseModel):
    name: str = Field(
        "Production API Key",
        description="Friendly name/label for the API key",
        examples=["Mobile App Backend", "Zapier Integration"],
    )


class ApiKeyResponse(BaseModel):
    id: str
    name: str
    token: str
    created_at: float
    is_active: bool = True


class ApiKeyListResponse(BaseModel):
    protection_enabled: bool
    total: int
    keys: List[ApiKeyResponse]


class ToggleProtectionRequest(BaseModel):
    enabled: bool = Field(..., description="Enable or disable mandatory API Key validation for decision endpoints")


class ToggleProtectionResponse(BaseModel):
    success: bool = True
    protection_enabled: bool
    message: str
