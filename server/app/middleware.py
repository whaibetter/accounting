import logging
import re
import time
from collections import defaultdict
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("accounting")

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_SCRIPT_PATTERN = re.compile(r"<\s*script", re.IGNORECASE)


class RateLimiter:
    def __init__(self, max_requests: int = 120, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    def check(self, client_ip: str) -> bool:
        now = time.time()
        hits = self._hits[client_ip]
        self._hits[client_ip] = [t for t in hits if now - t < self.window]
        if len(self._hits[client_ip]) >= self.max_requests:
            return False
        self._hits[client_ip].append(now)
        return True


_rate_limiter = RateLimiter()


def sanitize_string(value: str) -> str:
    if not isinstance(value, str):
        return value
    cleaned = _SCRIPT_PATTERN.sub("", value)
    cleaned = _CONTROL_CHARS.sub("", cleaned)
    return cleaned.strip()


async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    if not _rate_limiter.check(client_ip):
        return JSONResponse(
            status_code=429,
            content={"code": 429, "message": "请求过于频繁，请稍后再试", "data": None},
        )
    return await call_next(request)


async def audit_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    logger.info(
        f"{request.method} {request.url.path} "
        f"{response.status_code} {duration:.1f}ms "
        f"ip={request.client.host if request.client else 'unknown'}"
    )
    return response


async def error_shield_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logger.exception(f"Unhandled: {exc}")
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": "服务器内部错误", "data": None},
        )


def register_middlewares(app: FastAPI):
    app.middleware("http")(rate_limit_middleware)
    app.middleware("http")(audit_middleware)
    app.middleware("http")(error_shield_middleware)
