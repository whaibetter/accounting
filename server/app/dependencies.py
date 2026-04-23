from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth import verify_token

_security = HTTPBearer(auto_error=False)

PUBLIC_PATHS = {"/health", "/api/v1/auth/login", "/docs", "/redoc", "/openapi.json"}


async def require_auth(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(_security),
) -> str:
    if request.url.path in PUBLIC_PATHS:
        return ""

    if credentials is None:
        raise HTTPException(status_code=401, detail="未提供认证Token")

    device_id = verify_token(credentials.credentials, "access")
    if device_id is None:
        raise HTTPException(status_code=401, detail="Token无效或已过期")

    return device_id
