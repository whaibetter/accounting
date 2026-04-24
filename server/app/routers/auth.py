from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.auth import create_access_token, verify_password, change_password

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


class LoginRequest(BaseModel):
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
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
    if not change_password(req.old_password, req.new_password):
        raise HTTPException(status_code=401, detail="旧密码错误")
    return {
        "code": 200,
        "message": "密码修改成功",
        "data": None,
    }
