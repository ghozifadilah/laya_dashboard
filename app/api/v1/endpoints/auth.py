from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from app.schemas.auth import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    UserInfo,
)
from app.services.auth_service import (
    auth_service,
    get_current_user_optional,
    get_current_user_required,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login to obtain session token (default: admin / admin123)",
)
async def login(request: LoginRequest) -> LoginResponse:
    res = auth_service.authenticate(request.username, request.password)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah.",
        )
    return LoginResponse(
        success=True,
        token=res["token"],
        user=UserInfo(**res["user"]),
    )


@router.get(
    "/me",
    response_model=UserInfo,
    summary="Get current logged in user information",
)
async def get_me(user: Dict[str, Any] = Depends(get_current_user_required)) -> UserInfo:
    return UserInfo(**user)


@router.post(
    "/change-password",
    response_model=ChangePasswordResponse,
    summary="Change user password (persisted in JSON storage)",
)
async def change_password(
    request: ChangePasswordRequest,
    user: Dict[str, Any] = Depends(get_current_user_required),
) -> ChangePasswordResponse:
    try:
        auth_service.change_password(
            username=user["username"],
            old_password=request.old_password,
            new_password=request.new_password,
        )
        return ChangePasswordResponse(
            success=True,
            message="Password berhasil diubah.",
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Logout current session",
)
async def logout(authorization: Optional[str] = Header(None)) -> LogoutResponse:
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        auth_service.logout(token)
    return LogoutResponse(success=True, message="Logout berhasil.")
