import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import func

from app.auth import update_user_profile, get_user_by_id, _hash_password
from app.database import SessionLocal
from app.dependencies import require_admin
from app.models import User, OperationLog

logger = logging.getLogger("admin")

router = APIRouter(prefix="/api/v1/admin", tags=["后台管理"], dependencies=[Depends(require_admin)])


def _log_operation(db, operator_id: int, operator_name: str, action: str,
                   target_type: str = "", target_id: int = None,
                   detail: str = "", ip_address: str = ""):
    log = OperationLog(
        operator_id=operator_id,
        operator_name=operator_name,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail=detail,
        ip_address=ip_address,
    )
    db.add(log)
    db.commit()


@router.get("/users", summary="获取用户列表")
def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[int] = Query(None, ge=0, le=1, description="状态筛选"),
    is_admin: Optional[int] = Query(None, ge=0, le=1, description="管理员筛选"),
    admin_id: int = Depends(require_admin),
    request: Request = None,
):
    db = SessionLocal()
    try:
        query = db.query(User)
        if keyword:
            query = query.filter(
                (User.username.contains(keyword)) |
                (User.nickname.contains(keyword)) |
                (User.email.contains(keyword))
            )
        if status is not None:
            query = query.filter(User.status == status)
        if is_admin is not None:
            query = query.filter(User.is_admin == is_admin)

        total = query.count()
        users = query.order_by(User.id.desc()).offset((page - 1) * size).limit(size).all()

        items = []
        for u in users:
            items.append({
                "id": u.id,
                "username": u.username,
                "nickname": u.nickname,
                "avatar": u.avatar,
                "email": u.email,
                "phone": u.phone,
                "is_admin": u.is_admin,
                "status": u.status,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "updated_at": u.updated_at.isoformat() if u.updated_at else None,
            })

        return {
            "code": 200,
            "message": "success",
            "data": {
                "items": items,
                "total": total,
                "page": page,
                "size": size,
            },
        }
    finally:
        db.close()


@router.get("/users/{user_id}", summary="获取用户详情")
def get_user_detail(user_id: int, admin_id: int = Depends(require_admin)):
    profile = get_user_by_id(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"code": 200, "message": "success", "data": profile}


class AdminUpdateUserRequest(BaseModel):
    nickname: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    is_admin: int | None = Field(default=None, ge=0, le=1)
    status: int | None = Field(default=None, ge=0, le=1)
    password: str | None = Field(default=None, min_length=6)


@router.put("/users/{user_id}", summary="编辑用户信息")
def admin_update_user(
    user_id: int,
    req: AdminUpdateUserRequest,
    admin_id: int = Depends(require_admin),
    request: Request = None,
):
    kwargs = {k: v for k, v in req.model_dump().items() if v is not None and k != "password"}
    if req.password:
        hashed = _hash_password(req.password)
        kwargs["password_hash"] = hashed

    if not kwargs:
        raise HTTPException(status_code=400, detail="没有需要更新的字段")

    success, msg = update_user_profile(user_id, admin_mode=True, **kwargs)
    if not success:
        raise HTTPException(status_code=400, detail=msg)

    db = SessionLocal()
    try:
        admin_profile = get_user_by_id(admin_id)
        _log_operation(
            db, admin_id, admin_profile.get("username", "") if admin_profile else "",
            "update_user", "user", user_id,
            f"更新字段: {', '.join(kwargs.keys())}",
            request.client.host if request and request.client else "",
        )
    finally:
        db.close()

    profile = get_user_by_id(user_id)
    return {"code": 200, "message": "更新成功", "data": profile}


@router.delete("/users/{user_id}", summary="禁用用户")
def admin_disable_user(
    user_id: int,
    admin_id: int = Depends(require_admin),
    request: Request = None,
):
    if user_id == admin_id:
        raise HTTPException(status_code=400, detail="不能禁用自己")

    success, msg = update_user_profile(user_id, admin_mode=True, status=0)
    if not success:
        raise HTTPException(status_code=400, detail=msg)

    db = SessionLocal()
    try:
        admin_profile = get_user_by_id(admin_id)
        _log_operation(
            db, admin_id, admin_profile.get("username", "") if admin_profile else "",
            "disable_user", "user", user_id,
            "禁用用户",
            request.client.host if request and request.client else "",
        )
    finally:
        db.close()

    return {"code": 200, "message": "用户已禁用", "data": None}


@router.get("/logs", summary="获取操作日志")
def list_operation_logs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    action: Optional[str] = Query(None, description="操作类型筛选"),
    operator_name: Optional[str] = Query(None, description="操作人筛选"),
    admin_id: int = Depends(require_admin),
):
    db = SessionLocal()
    try:
        query = db.query(OperationLog)
        if action:
            query = query.filter(OperationLog.action == action)
        if operator_name:
            query = query.filter(OperationLog.operator_name.contains(operator_name))

        total = query.count()
        logs = query.order_by(OperationLog.id.desc()).offset((page - 1) * size).limit(size).all()

        items = []
        for log in logs:
            items.append({
                "id": log.id,
                "operator_id": log.operator_id,
                "operator_name": log.operator_name,
                "action": log.action,
                "target_type": log.target_type,
                "target_id": log.target_id,
                "detail": log.detail,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            })

        return {
            "code": 200,
            "message": "success",
            "data": {
                "items": items,
                "total": total,
                "page": page,
                "size": size,
            },
        }
    finally:
        db.close()


@router.get("/stats", summary="管理后台统计")
def admin_stats(admin_id: int = Depends(require_admin)):
    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.status == 1).count()
        admin_count = db.query(User).filter(User.is_admin == 1).count()
        disabled_users = db.query(User).filter(User.status == 0).count()

        from app.models import Bill, Account
        total_bills = db.query(Bill).count()
        total_accounts = db.query(Account).count()

        return {
            "code": 200,
            "message": "success",
            "data": {
                "total_users": total_users,
                "active_users": active_users,
                "admin_count": admin_count,
                "disabled_users": disabled_users,
                "total_bills": total_bills,
                "total_accounts": total_accounts,
            },
        }
    finally:
        db.close()
