import bcrypt
import logging
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

from app.database import SessionLocal

logger = logging.getLogger("auth")

DEFAULT_EXPENSE_CATEGORIES = [
    ("餐饮", "food", ["早餐", "午餐", "晚餐", "零食", "饮料"]),
    ("交通", "transport", ["公交", "地铁", "打车", "加油", "停车"]),
    ("购物", "shopping", ["日用品", "衣物", "数码", "美妆"]),
    ("居住", "housing", ["房租", "水电", "物业", "网费"]),
    ("娱乐", "entertainment", ["电影", "游戏", "旅行", "运动"]),
    ("医疗", "medical", ["门诊", "药品", "体检"]),
    ("教育", "education", ["书籍", "课程", "培训"]),
    ("通讯", "telecom", ["话费", "会员"]),
    ("人情", "social", ["红包", "礼物", "请客"]),
    ("其他", "other_expense", []),
]

DEFAULT_INCOME_CATEGORIES = [
    ("工资", "salary", []),
    ("兼职", "parttime", []),
    ("理财", "investment", []),
    ("红包", "redpacket", []),
    ("退款", "refund", []),
    ("其他", "other_income", []),
]


def _seed_user_categories(db, user_id: int):
    from app.models import Category
    sort = 0
    for name, icon, children in DEFAULT_EXPENSE_CATEGORIES:
        parent = Category(user_id=user_id, name=name, type=1, icon=icon, sort_order=sort)
        db.add(parent)
        db.flush()
        for child_name in children:
            db.add(Category(user_id=user_id, name=child_name, type=1, parent_id=parent.id, sort_order=sort))
        sort += 1
    for name, icon, children in DEFAULT_INCOME_CATEGORIES:
        parent = Category(user_id=user_id, name=name, type=2, icon=icon, sort_order=sort)
        db.add(parent)
        db.flush()
        for child_name in children:
            db.add(Category(user_id=user_id, name=child_name, type=2, parent_id=parent.id, sort_order=sort))
        sort += 1
    db.commit()


def _seed_user_account(db, user_id: int):
    from app.models import Account
    default = Account(
        user_id=user_id, name="现金", type=1, icon="cash",
        color="#4CAF50", balance=0, initial_balance=0,
        is_default=1, sort_order=0,
    )
    db.add(default)
    db.commit()

ALGORITHM = "HS256"
ACCESS_EXPIRE_DAYS = 7

_SECRET_KEY_NAME = "jwt_secret_key"


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


def _init_secret_key() -> None:
    if _get_config_value(_SECRET_KEY_NAME) is not None:
        return
    key = secrets.token_hex(32)
    _set_config_value(_SECRET_KEY_NAME, key)


def init_auth() -> None:
    _init_secret_key()
    _migrate_legacy_data()
    _ensure_default_admin()


def get_secret_key() -> str:
    key = _get_config_value(_SECRET_KEY_NAME)
    if not key:
        _init_secret_key()
        key = _get_config_value(_SECRET_KEY_NAME)
    return key


def _migrate_legacy_data() -> None:
    import os
    legacy_password_file = os.path.join(os.path.dirname(__file__), "..", "data", ".access_password")
    legacy_secret_file = os.path.join(os.path.dirname(__file__), "..", "data", ".secret_key")

    if os.path.exists(legacy_password_file):
        try:
            with open(legacy_password_file, "r") as f:
                old_hash = f.read().strip()
            if old_hash:
                db = SessionLocal()
                try:
                    from app.models import User
                    existing = db.query(User).first()
                    if not existing:
                        user = User(
                            username="admin",
                            password_hash=old_hash if old_hash.startswith("$2b$") else f"sha256:{old_hash}",
                            nickname="管理员",
                        )
                        db.add(user)
                        db.commit()
                        logger.info("已从旧密码文件迁移为默认admin用户")
                finally:
                    db.close()
            os.replace(legacy_password_file, legacy_password_file + ".bak")
        except Exception as e:
            logger.warning(f"迁移旧密码文件失败: {e}")

    if os.path.exists(legacy_secret_file):
        try:
            with open(legacy_secret_file, "r") as f:
                old_key = f.read().strip()
            if old_key and not _get_config_value(_SECRET_KEY_NAME):
                _set_config_value(_SECRET_KEY_NAME, old_key)
            os.replace(legacy_secret_file, legacy_secret_file + ".bak")
        except Exception as e:
            logger.warning(f"迁移旧密钥文件失败: {e}")

    db = SessionLocal()
    try:
        from app.models import SystemConfig
        stored = db.query(SystemConfig).filter(SystemConfig.key == "password_hash").first()
        if stored:
            existing_user = db.query(User).filter(User.username == "admin").first()
            if not existing_user:
                user = User(
                    username="admin",
                    password_hash=stored.value,
                    nickname="管理员",
                )
                db.add(user)
                db.commit()
                logger.info("已从system_config迁移密码为默认admin用户")
            db.delete(stored)
            db.commit()
    except Exception as e:
        logger.warning(f"迁移system_config密码失败: {e}")
    finally:
        db.close()


def _ensure_default_admin() -> None:
    """确保至少存在一个管理员账户，并为没有分类的用户补充默认数据"""
    db = SessionLocal()
    try:
        from app.models import User, Category, Account
        admin_exists = db.query(User).filter(User.is_admin == 1).first()
        if not admin_exists:
            hashed = _hash_password("a6e823c5")
            admin = User(
                username="admin",
                password_hash=hashed,
                nickname="管理员",
                is_admin=1,
                status=1,
            )
            db.add(admin)
            db.commit()
            logger.info("已创建默认管理员账户: admin")

        users_without_categories = db.query(User).filter(
            ~User.id.in_(db.query(Category.user_id).distinct())
        ).all()
        for user in users_without_categories:
            _seed_user_categories(db, user.id)
            logger.info(f"已为用户 {user.username} 补充默认分类")

        users_without_accounts = db.query(User).filter(
            ~User.id.in_(db.query(Account.user_id).distinct())
        ).all()
        for user in users_without_accounts:
            _seed_user_account(db, user.id)
            logger.info(f"已为用户 {user.username} 补充默认账户")
    except Exception as e:
        db.rollback()
        logger.warning(f"初始化默认数据失败: {e}")
    finally:
        db.close()


def check_username(username: str) -> tuple[bool, str]:
    if not username or len(username) < 3:
        return False, "用户名长度不能少于3位"
    if len(username) > 50:
        return False, "用户名长度不能超过50位"
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "用户名只能包含字母、数字和下划线"
    return True, ""


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


def register_user(username: str, password: str) -> tuple[Optional[int], str]:
    valid, msg = check_username(username)
    if not valid:
        return None, msg
    valid, msg = check_password_strength(password)
    if not valid:
        return None, msg

    db = SessionLocal()
    try:
        from app.models import User
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            return None, "用户名已存在"
        hashed = _hash_password(password)
        user = User(username=username, password_hash=hashed, nickname=username)
        db.add(user)
        db.commit()
        db.refresh(user)
        _seed_user_categories(db, user.id)
        _seed_user_account(db, user.id)
        logger.info(f"新用户注册: {username}")
        return user.id, "注册成功"
    except Exception as e:
        db.rollback()
        logger.error(f"注册失败: {e}")
        return None, "注册失败"
    finally:
        db.close()


def authenticate_user(username: str, password: str) -> tuple[Optional[int], str]:
    if not username or not password:
        return None, "请输入用户名和密码"

    db = SessionLocal()
    try:
        from app.models import User
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None, "用户名或密码错误"

        stored = user.password_hash
        if stored.startswith("sha256:"):
            import hashlib
            legacy_hash = stored[7:]
            if hashlib.sha256(password.encode("utf-8")).hexdigest() == legacy_hash:
                user.password_hash = _hash_password(password)
                db.commit()
                logger.info(f"用户 {username} 密码已从SHA-256升级为bcrypt")
                return user.id, "登录成功"
            return None, "用户名或密码错误"

        if _verify_bcrypt(password, stored):
            return user.id, "登录成功"
        return None, "用户名或密码错误"
    finally:
        db.close()


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_EXPIRE_DAYS)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire, "type": "access"},
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


def get_user_by_id(user_id: int) -> Optional[dict]:
    db = SessionLocal()
    try:
        from app.models import User
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        return {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "email": user.email,
            "phone": user.phone,
            "is_admin": user.is_admin,
            "status": user.status,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }
    finally:
        db.close()


def update_user_profile(user_id: int, admin_mode: bool = False, **kwargs) -> tuple[bool, str]:
    db = SessionLocal()
    try:
        from app.models import User
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "用户不存在"

        if admin_mode:
            allowed_fields = {"nickname", "avatar", "email", "phone", "is_admin", "status"}
        else:
            allowed_fields = {"nickname", "avatar", "email", "phone"}
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(user, key, value)

        db.commit()
        return True, "更新成功"
    except Exception as e:
        db.rollback()
        return False, f"更新失败: {str(e)}"
    finally:
        db.close()


def change_user_password(user_id: int, old_password: str, new_password: str) -> tuple[bool, str]:
    db = SessionLocal()
    try:
        from app.models import User
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "用户不存在"

        stored = user.password_hash
        if stored.startswith("sha256:"):
            import hashlib
            legacy_hash = stored[7:]
            if hashlib.sha256(old_password.encode("utf-8")).hexdigest() != legacy_hash:
                return False, "旧密码错误"
        else:
            if not _verify_bcrypt(old_password, stored):
                return False, "旧密码错误"

        valid, msg = check_password_strength(new_password)
        if not valid:
            return False, msg
        if old_password == new_password:
            return False, "新密码不能与旧密码相同"

        user.password_hash = _hash_password(new_password)
        db.commit()
        logger.info(f"用户ID {user_id} 修改密码成功")
        return True, "密码修改成功"
    except Exception as e:
        db.rollback()
        return False, f"修改密码失败: {str(e)}"
    finally:
        db.close()
