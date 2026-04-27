from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.auth import (
    create_access_token, authenticate_user, register_user,
    get_user_by_id, update_user_profile, change_user_password,
)
from app.dependencies import require_auth

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UpdateProfileRequest(BaseModel):
    nickname: str | None = Field(default=None, max_length=50)
    avatar: str | None = Field(default=None, max_length=200)
    email: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)


@router.post("/register", summary="用户注册")
def register(req: RegisterRequest):
    user_id, msg = register_user(req.username, req.password)
    if user_id is None:
        raise HTTPException(status_code=400, detail=msg)
    access_token = create_access_token(user_id)
    return {
        "code": 200,
        "message": msg,
        "data": {
            "access_token": access_token,
            "user_id": user_id,
        },
    }


@router.post("/login", summary="用户登录")
def login(req: LoginRequest):
    user_id, msg = authenticate_user(req.username, req.password)
    if user_id is None:
        raise HTTPException(status_code=401, detail=msg)
    access_token = create_access_token(user_id)
    return {
        "code": 200,
        "message": msg,
        "data": {
            "access_token": access_token,
            "user_id": user_id,
        },
    }


@router.get("/profile", summary="获取个人信息")
def get_profile(user_id: int = Depends(require_auth)):
    profile = get_user_by_id(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {
        "code": 200,
        "message": "success",
        "data": profile,
    }


@router.put("/profile", summary="更新个人信息")
def update_profile(req: UpdateProfileRequest, user_id: int = Depends(require_auth)):
    kwargs = {k: v for k, v in req.model_dump().items() if v is not None}
    if not kwargs:
        raise HTTPException(status_code=400, detail="没有需要更新的字段")
    success, msg = update_user_profile(user_id, **kwargs)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    profile = get_user_by_id(user_id)
    return {
        "code": 200,
        "message": msg,
        "data": profile,
    }


@router.post("/change-password", summary="修改密码")
def change_password_api(req: ChangePasswordRequest, user_id: int = Depends(require_auth)):
    success, msg = change_user_password(user_id, req.old_password, req.new_password)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {
        "code": 200,
        "message": msg,
        "data": None,
    }
