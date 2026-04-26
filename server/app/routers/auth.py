"""
认证路由模块。

提供以下接口：
    - POST /login          密码登录
    - POST /change-password  修改密码（需旧密码验证）
    - POST /reset-password   重置密码（管理员操作，需认证）
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.auth import create_access_token, verify_password, change_password, reset_password, check_password_strength
from app.dependencies import require_auth

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


class LoginRequest(BaseModel):
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class ResetPasswordRequest(BaseModel):
    new_password: str


@router.post("/login", summary="密码登录")
def login(req: LoginRequest):
    if not verify_password(req.password):
        raise HTTPException(status_code=401, detail="密码错误")
    access_token = create_access_token()
    return {
        "code": 200,
        "message": "success",
        "data": {
            "access_token": access_token,
        },
    }


@router.post("/change-password", summary="修改密码")
def change_password_api(req: ChangePasswordRequest):
    success, msg = change_password(req.old_password, req.new_password)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {
        "code": 200,
        "message": msg,
        "data": None,
    }


@router.post("/reset-password", summary="重置密码（需认证）")
def reset_password_api(req: ResetPasswordRequest, _user: str = Depends(require_auth)):
    valid, msg = check_password_strength(req.new_password)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)
    success, msg = reset_password(req.new_password)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {
        "code": 200,
        "message": msg,
        "data": None,
    }
