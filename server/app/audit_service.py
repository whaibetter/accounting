import json
import logging
import time
from datetime import datetime
from typing import Optional

from app.database import SessionLocal
from app.models import OperationLog

logger = logging.getLogger("audit")

SKIP_PATHS = {
    "/health", "/docs", "/redoc", "/openapi.json",
    "/api/v1/auth/login", "/api/v1/auth/register",
}

ACTION_MAP = {
    "POST": "create",
    "PUT": "update",
    "DELETE": "delete",
    "GET": "read",
}

TARGET_TYPE_MAP = {
    "/api/v1/accounts": "account",
    "/api/v1/bills": "bill",
    "/api/v1/categories": "category",
    "/api/v1/tags": "tag",
    "/api/v1/auth": "auth",
    "/api/v1/llm": "llm",
    "/api/v1/admin": "admin",
    "/api/v1/import": "import",
    "/api/v1/export": "export",
    "/api/v1/avatar": "avatar",
    "/api/v1/statistics": "statistics",
}


def _resolve_target_type(path: str) -> str:
    for prefix, ttype in TARGET_TYPE_MAP.items():
        if path.startswith(prefix):
            return ttype
    return "system"


def _resolve_action(method: str, path: str) -> str:
    if method in ("POST", "PUT", "DELETE"):
        return ACTION_MAP.get(method, method.lower())

    if "/export" in path:
        return "export"
    if "/import" in path:
        return "import"
    if "/test" in path or "/stream" in path:
        return "ai_test"
    if "/parse" in path:
        return "ai_parse"
    if "/config" in path:
        return "read_config"
    if "/statistics" in path or "/stats" in path or "/overview" in path or "/trend" in path:
        return "statistics"
    if "/profile" in path:
        return "read_profile"
    if "/logs" in path:
        return "read_logs"

    return "read"


def log_operation(
    operator_id: int,
    operator_name: str,
    action: str,
    target_type: str = "",
    target_id: int = None,
    detail: str = "",
    ip_address: str = "",
    method: str = "",
    path: str = "",
    status: str = "success",
    duration_ms: int = None,
    extra_data: dict = None,
):
    try:
        db = SessionLocal()
        try:
            log = OperationLog(
                operator_id=operator_id or 0,
                operator_name=operator_name or "anonymous",
                action=action,
                target_type=target_type,
                target_id=target_id,
                detail=detail[:500] if detail else "",
                ip_address=ip_address,
                method=method,
                path=path[:200] if path else "",
                status=status,
                duration_ms=duration_ms,
                extra_data=json.dumps(extra_data, ensure_ascii=False) if extra_data else None,
            )
            db.add(log)
            db.commit()
        finally:
            db.close()
    except Exception as e:
        logger.error(f"记录操作日志失败: {e}")


def log_from_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user_id: int = 0,
    username: str = "",
    ip_address: str = "",
    detail: str = "",
    extra_data: dict = None,
):
    if path in SKIP_PATHS:
        return
    if path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/openapi"):
        return

    action = _resolve_action(method, path)
    target_type = _resolve_target_type(path)
    status = "success" if 200 <= status_code < 400 else "failure"

    log_operation(
        operator_id=user_id,
        operator_name=username,
        action=action,
        target_type=target_type,
        detail=detail,
        ip_address=ip_address,
        method=method,
        path=path,
        status=status,
        duration_ms=int(duration_ms),
        extra_data=extra_data,
    )
