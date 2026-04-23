from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.auth import create_access_token, verify_password

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


class LoginRequest(BaseModel):
    password: str


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
