"""
认证与密码管理模块。

功能描述：
    - 使用 bcrypt 算法进行密码哈希与验证
    - 密码和 JWT 密钥存储在数据库 system_config 表中
    - 支持密码创建、验证、更新操作
    - 提供密码强度校验
    - 记录密码操作审计日志

迁移说明：
    - 旧版使用 SHA-256（无盐）+ 文件存储，已废弃
    - 首次启动时自动从旧文件迁移密码到数据库
"""

import bcrypt
import logging
import os
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

from app.database import SessionLocal

logger = logging.getLogger("auth")

ALGORITHM = "HS256"
ACCESS_EXPIRE_DAYS = 7

_PASSWORD_KEY = "password_hash"
_SECRET_KEY_NAME = "jwt_secret_key"

_LEGACY_PASSWORD_FILE = os.path.join(os.path.dirname(__file__), "..", "data", ".access_password")
_LEGACY_SECRET_FILE = os.path.join(os.path.dirname(__file__), "..", "data", ".secret_key")


def _get_config_value(key: str) -> Optional[str]:
    db = SessionLocal()
    try:
        from app.models import SystemConfig
        row = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        return row.value if row else None
    finally:
        db.close()


def _set_config_value(key: str, value: str) -> None:
    db = SessionLocal()
    try:
        from app.models import SystemConfig
        row = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if row:
            row.value = value
            row.updated_at = datetime.now()
        else:
            row = SystemConfig(key=key, value=value)
            db.add(row)
        db.commit()
    finally:
        db.close()


def _hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def _verify_bcrypt(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def _verify_legacy_sha256(password: str, hashed: str) -> bool:
    import hashlib
    return hashlib.sha256(password.encode("utf-8")).hexdigest() == hashed


def _migrate_from_files() -> None:
    if os.path.exists(_LEGACY_PASSWORD_FILE):
        try:
            with open(_LEGACY_PASSWORD_FILE, "r") as f:
                old_hash = f.read().strip()
            if old_hash and not _get_config_value(_PASSWORD_KEY):
                _set_config_value(_PASSWORD_KEY, f"sha256:{old_hash}")
                logger.info("已从旧文件迁移密码哈希到数据库（SHA-256 格式，将在下次修改密码时自动升级为 bcrypt）")
            os.rename(_LEGACY_PASSWORD_FILE, _LEGACY_PASSWORD_FILE + ".bak")
            logger.info("旧密码文件已备份为 .access_password.bak")
        except Exception as e:
            logger.warning(f"迁移旧密码文件失败: {e}")

    if os.path.exists(_LEGACY_SECRET_FILE):
        try:
            with open(_LEGACY_SECRET_FILE, "r") as f:
                old_key = f.read().strip()
            if old_key and not _get_config_value(_SECRET_KEY_NAME):
                _set_config_value(_SECRET_KEY_NAME, old_key)
                logger.info("已从旧文件迁移 JWT 密钥到数据库")
            os.rename(_LEGACY_SECRET_FILE, _LEGACY_SECRET_FILE + ".bak")
            logger.info("旧密钥文件已备份为 .secret_key.bak")
        except Exception as e:
            logger.warning(f"迁移旧密钥文件失败: {e}")


def _init_password() -> None:
    if _get_config_value(_PASSWORD_KEY) is not None:
        return
    plain = secrets.token_hex(4)
    hashed = _hash_password(plain)
    _set_config_value(_PASSWORD_KEY, hashed)
    logger.info(f"系统访问密码已自动生成: {plain}")
    logger.info("请妥善保管此密码，它不会再次显示")
    print(f"\n[auth] 系统访问密码已自动生成: {plain}")
    print("[auth] 请妥善保管此密码，它不会再次显示\n")


def _init_secret_key() -> None:
    if _get_config_value(_SECRET_KEY_NAME) is not None:
        return
    key = secrets.token_hex(32)
    _set_config_value(_SECRET_KEY_NAME, key)


def init_auth() -> None:
    _migrate_from_files()
    _init_password()
    _init_secret_key()


def get_secret_key() -> str:
    key = _get_config_value(_SECRET_KEY_NAME)
    if not key:
        _init_secret_key()
        key = _get_config_value(_SECRET_KEY_NAME)
    return key


def verify_password(password: str) -> bool:
    stored = _get_config_value(_PASSWORD_KEY)
    if not stored:
        return False
    if stored.startswith("sha256:"):
        legacy_hash = stored[7:]
        if _verify_legacy_sha256(password, legacy_hash):
            new_hash = _hash_password(password)
            _set_config_value(_PASSWORD_KEY, new_hash)
            logger.info("密码已从 SHA-256 自动升级为 bcrypt")
            return True
        return False
    return _verify_bcrypt(password, stored)


def check_password_strength(password: str) -> tuple[bool, str]:
    if len(password) < 6:
        return False, "密码长度不能少于6位"
    if len(password) > 128:
        return False, "密码长度不能超过128位"
    if re.search(r"[\u4e00-\u9fff]", password):
        return False, "密码不能包含中文字符"
    has_letter = bool(re.search(r"[a-zA-Z]", password))
    has_digit = bool(re.search(r"\d", password))
    if not has_letter or not has_digit:
        return False, "密码需同时包含字母和数字"
    return True, ""


def change_password(old_password: str, new_password: str) -> tuple[bool, str]:
    if not verify_password(old_password):
        return False, "旧密码错误"
    valid, msg = check_password_strength(new_password)
    if not valid:
        return False, msg
    if old_password == new_password:
        return False, "新密码不能与旧密码相同"
    hashed = _hash_password(new_password)
    _set_config_value(_PASSWORD_KEY, hashed)
    logger.info("密码已修改（bcrypt 哈希）")
    return True, "密码修改成功"


def reset_password(new_password: str) -> tuple[bool, str]:
    valid, msg = check_password_strength(new_password)
    if not valid:
        return False, msg
    hashed = _hash_password(new_password)
    _set_config_value(_PASSWORD_KEY, hashed)
    logger.info("密码已由管理员重置（bcrypt 哈希）")
    return True, "密码重置成功"


def create_access_token() -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_EXPIRE_DAYS)
    return jwt.encode(
        {"sub": "user", "exp": expire, "type": "access"},
        get_secret_key(),
        algorithm=ALGORITHM,
    )


def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            return None
        return payload.get("sub")
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
