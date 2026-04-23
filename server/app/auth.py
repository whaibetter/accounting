import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

_SECRET_FILE = os.path.join(os.path.dirname(__file__), "..", "data", ".secret_key")
_PASSWORD_FILE = os.path.join(os.path.dirname(__file__), "..", "data", ".access_password")
ALGORITHM = "HS256"
ACCESS_EXPIRE_DAYS = 7


def _get_secret_key() -> str:
    if os.path.exists(_SECRET_FILE):
        with open(_SECRET_FILE, "r") as f:
            key = f.read().strip()
            if key:
                return key
    key = secrets.token_hex(32)
    os.makedirs(os.path.dirname(_SECRET_FILE), exist_ok=True)
    with open(_SECRET_FILE, "w") as f:
        f.write(key)
    os.chmod(_SECRET_FILE, 0o600)
    return key


SECRET_KEY = _get_secret_key()


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_or_init_password() -> str:
    if os.path.exists(_PASSWORD_FILE):
        with open(_PASSWORD_FILE, "r") as f:
            hashed = f.read().strip()
            if hashed:
                return hashed
    plain = secrets.token_hex(4)
    hashed = _hash_password(plain)
    os.makedirs(os.path.dirname(_PASSWORD_FILE), exist_ok=True)
    with open(_PASSWORD_FILE, "w") as f:
        f.write(hashed)
    os.chmod(_PASSWORD_FILE, 0o600)
    print(f"[auth] 系统访问密码已自动生成: {plain}")
    print(f"[auth] 请妥善保管此密码，它不会再次显示")
    return hashed


PASSWORD_HASH = get_or_init_password()


def verify_password(password: str) -> bool:
    return _hash_password(password) == PASSWORD_HASH


def create_access_token() -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_EXPIRE_DAYS)
    return jwt.encode(
        {"sub": "user", "exp": expire, "type": "access"},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            return None
        return payload.get("sub")
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
