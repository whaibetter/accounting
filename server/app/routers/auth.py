"""
认证路由模块。

提供以下接口：
    - POST /login          用户登录
    - POST /register       用户注册
    - GET  /profile        获取当前用户信息
    - PUT  /profile        更新当前用户信息
    - POST /change-password 修改密码
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.auth import (
    authenticate_user,
    register_user,
    create_access_token,
    get_user_by_id,
    update_user_profile,
    change_user_password,
    check_password_strength,
)
from app.dependencies import require_auth

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


class ProfileUpdateRequest(BaseModel):
    nickname: Optional[str] = Field(default=None, max_length=50)
    avatar: Optional[str] = None
    email: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.post("/login", summary="用户登录")
def login(req: LoginRequest):
    user_id, msg = authenticate_user(req.username, req.password)
    if not user_id:
        raise HTTPException(status_code=401, detail=msg)
    
    profile = get_user_by_id(user_id)
    if profile and profile.get("status") == 0:
        raise HTTPException(status_code=403, detail="账户已被禁用")
    
    access_token = create_access_token(user_id)
    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "access_token": access_token,
            "user": profile,
        },
    }


@router.post("/register", summary="用户注册")
def register(req: RegisterRequest):
    user_id, msg = register_user(req.username, req.password)
    if not user_id:
        raise HTTPException(status_code=400, detail=msg)
    
    access_token = create_access_token(user_id)
    profile = get_user_by_id(user_id)
    return {
        "code": 200,
        "message": "注册成功",
        "data": {
            "access_token": access_token,
            "user": profile,
        },
    }


@router.get("/profile", summary="获取当前用户信息")
def get_profile(user_id: int = Depends(require_auth)):
    profile = get_user_by_id(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {
        "code": 200,
        "message": "success",
        "data": profile,
    }


@router.put("/profile", summary="更新当前用户信息")
def update_profile(req: ProfileUpdateRequest, user_id: int = Depends(require_auth)):
    data = req.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="没有需要更新的字段")
    
    success, msg = update_user_profile(user_id, **data)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    
    profile = get_user_by_id(user_id)
    return {
        "code": 200,
        "message": msg,
        "data": profile,
    }


@router.post("/change-password", summary="修改密码")
def change_password(req: ChangePasswordRequest, user_id: int = Depends(require_auth)):
    success, msg = change_user_password(user_id, req.old_password, req.new_password)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {
        "code": 200,
        "message": msg,
        "data": None,
    }
