from typing import Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., description="Username (default: admin)", examples=["admin"])
    password: str = Field(..., description="Password (default: admin123)", examples=["admin123"])


class UserInfo(BaseModel):
    username: str
    name: str
    role: str


class LoginResponse(BaseModel):
    success: bool = True
    token: str = Field(..., description="Bearer session token")
    user: UserInfo


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., description="New password (min 4 characters)")


class ChangePasswordResponse(BaseModel):
    success: bool = True
    message: str


class LogoutResponse(BaseModel):
    success: bool = True
    message: str
