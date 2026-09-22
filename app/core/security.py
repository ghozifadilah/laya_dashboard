from typing import Any, Dict, Optional
from fastapi import Header, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings
from app.services.api_key_service import api_key_service
from app.services.auth_service import auth_service

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(
    x_api_key: Optional[str] = Security(API_KEY_HEADER),
    authorization: Optional[str] = Header(None),
) -> Optional[str]:
    """Verify API Key or active user session for decision endpoints.
    
    Accepts:
    1. Header `X-API-Key: laya_live_...`
    2. Header `Authorization: Bearer laya_live_...`
    3. User session bearer token from login.
    """
    # 1. Check if global protection is active
    protection_enabled = api_key_service.is_protection_enabled()
    if not protection_enabled and not settings.API_KEY_ENABLED:
        return None

    # 2. Extract token from either X-API-Key or Authorization header
    token = None
    if x_api_key:
        token = x_api_key.strip()
    elif authorization:
        token = authorization.replace("Bearer ", "").strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Akses ditolak: Endpoint ini diproteksi API Key. Sertakan header 'X-API-Key: <token>' atau 'Authorization: Bearer <token>'.",
        )

    # 3. Check if valid API Key
    if api_key_service.validate_token(token):
        return token

    # 4. Check if valid User Session
    user = auth_service.get_user_by_token(token)
    if user:
        return token

    # 5. Check if in static settings.API_KEYS list
    if settings.API_KEYS and token in settings.API_KEYS:
        return token

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="API Key atau token autentikasi tidak valid atau telah dinonaktifkan.",
    )
