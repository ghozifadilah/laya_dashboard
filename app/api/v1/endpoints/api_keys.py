from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Path, status
from app.schemas.api_keys import (
    ApiKeyCreateRequest,
    ApiKeyListResponse,
    ApiKeyResponse,
    ToggleProtectionRequest,
    ToggleProtectionResponse,
)
from app.services.api_key_service import api_key_service
from app.services.auth_service import get_current_user_required

router = APIRouter(prefix="/api-keys", tags=["API Key Management"])


@router.get(
    "",
    response_model=ApiKeyListResponse,
    summary="List all generated API Keys and protection status",
)
@router.get(
    "/",
    response_model=ApiKeyListResponse,
    include_in_schema=False,
)
async def list_api_keys(
    user: Dict[str, Any] = Depends(get_current_user_required),
) -> ApiKeyListResponse:
    keys = api_key_service.list_keys()
    protection = api_key_service.is_protection_enabled()
    return ApiKeyListResponse(
        protection_enabled=protection,
        total=len(keys),
        keys=[ApiKeyResponse(**k) for k in keys],
    )


@router.post(
    "",
    response_model=ApiKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a new secure API Key/Token",
)
@router.post(
    "/",
    response_model=ApiKeyResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def generate_api_key(
    request: ApiKeyCreateRequest,
    user: Dict[str, Any] = Depends(get_current_user_required),
) -> ApiKeyResponse:
    key = api_key_service.generate_key(name=request.name)
    return ApiKeyResponse(**key)


@router.delete(
    "/{key_id}",
    summary="Revoke / delete an API Key",
)
async def delete_api_key(
    key_id: str = Path(..., description="Key ID or token string to revoke"),
    user: Dict[str, Any] = Depends(get_current_user_required),
) -> Dict[str, Any]:
    deleted = api_key_service.delete_key(key_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API Key '{key_id}' tidak ditemukan.",
        )
    return {"success": True, "message": f"API Key '{key_id}' berhasil dihapus/direvoke."}


@router.post(
    "/toggle-protection",
    response_model=ToggleProtectionResponse,
    summary="Toggle global API Token protection requirement",
)
async def toggle_api_protection(
    request: ToggleProtectionRequest,
    user: Dict[str, Any] = Depends(get_current_user_required),
) -> ToggleProtectionResponse:
    state = api_key_service.toggle_protection(request.enabled)
    msg = (
        "Proteksi API Token AKTIF. Semua request eksternal wajib menyertakan API Key."
        if state
        else "Proteksi API Token NONAKTIF. Endpoint dapat diakses publik tanpa API Key."
    )
    return ToggleProtectionResponse(
        success=True,
        protection_enabled=state,
        message=msg,
    )
