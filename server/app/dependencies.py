from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth import verify_token, get_user_by_id

_security = HTTPBearer(auto_error=False)

PUBLIC_PATHS = {
    "/health",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/docs",
    "/redoc",
    "/openapi.json",
}

# 头像文件路径模式（支持通配符匹配）
PUBLIC_PATH_PATTERNS = [
    "/api/v1/avatar/file/",
]


async def require_auth(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(_security),
) -> int:
    path = request.url.path

    if path in PUBLIC_PATHS:
        return 0

    # 检查路径模式
    for pattern in PUBLIC_PATH_PATTERNS:
        if path.startswith(pattern):
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

    profile = get_user_by_id(user_id)
    if profile and profile.get("status") == 0:
        raise HTTPException(status_code=403, detail="账户已被禁用")

    return user_id


async def require_admin(
    user_id: int = Depends(require_auth),
) -> int:
    profile = get_user_by_id(user_id)
    if not profile or not profile.get("is_admin"):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user_id
