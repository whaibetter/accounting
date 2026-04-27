from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth import verify_token

_security = HTTPBearer(auto_error=False)

PUBLIC_PATHS = {
    "/health",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/docs",
    "/redoc",
    "/openapi.json",
}


async def require_auth(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(_security),
) -> int:
    if request.url.path in PUBLIC_PATHS:
        return 0

    if credentials is None:
        raise HTTPException(status_code=401, detail="未提供认证Token")

    user_id_str = verify_token(credentials.credentials, "access")
    if user_id_str is None:
        raise HTTPException(status_code=401, detail="Token无效或已过期")

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Token无效")

    return user_id
