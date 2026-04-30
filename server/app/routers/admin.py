import io
import json
import logging
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, or_

from app.auth import update_user_profile, get_user_by_id, _hash_password
from app.database import SessionLocal
from app.dependencies import require_admin
from app.models import User, OperationLog, Bill, Account, Category

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
    target_type: Optional[str] = Query(None, description="操作对象类型筛选"),
    operator_name: Optional[str] = Query(None, description="操作人筛选"),
    status: Optional[str] = Query(None, description="状态筛选 success/failure"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    keyword: Optional[str] = Query(None, description="关键词搜索(详情/路径)"),
    admin_id: int = Depends(require_admin),
):
    db = SessionLocal()
    try:
        query = db.query(OperationLog)
        if action:
            actions = [a.strip() for a in action.split(",")]
            if len(actions) == 1:
                query = query.filter(OperationLog.action == actions[0])
            else:
                query = query.filter(OperationLog.action.in_(actions))
        if target_type:
            query = query.filter(OperationLog.target_type == target_type)
        if operator_name:
            query = query.filter(OperationLog.operator_name.contains(operator_name))
        if status:
            query = query.filter(OperationLog.status == status)
        if start_date:
            try:
                sd = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(OperationLog.created_at >= sd)
            except ValueError:
                pass
        if end_date:
            try:
                ed = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
                query = query.filter(OperationLog.created_at <= ed)
            except ValueError:
                pass
        if keyword:
            kw = f"%{keyword}%"
            query = query.filter(
                or_(
                    OperationLog.detail.like(kw),
                    OperationLog.path.like(kw),
                    OperationLog.action.like(kw),
                )
            )

        total = query.count()
        logs = query.order_by(OperationLog.id.desc()).offset((page - 1) * size).limit(size).all()

        items = []
        for log in logs:
            item = {
                "id": log.id,
                "operator_id": log.operator_id,
                "operator_name": log.operator_name,
                "action": log.action,
                "target_type": log.target_type,
                "target_id": log.target_id,
                "detail": log.detail,
                "ip_address": log.ip_address,
                "method": log.method,
                "path": log.path,
                "status": log.status,
                "duration_ms": log.duration_ms,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            if log.extra_data:
                try:
                    item["extra_data"] = json.loads(log.extra_data)
                except (json.JSONDecodeError, TypeError):
                    item["extra_data"] = log.extra_data
            items.append(item)

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


@router.get("/logs/export", summary="导出操作日志")
def export_operation_logs(
    action: Optional[str] = Query(None, description="操作类型筛选"),
    target_type: Optional[str] = Query(None, description="操作对象类型筛选"),
    operator_name: Optional[str] = Query(None, description="操作人筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    admin_id: int = Depends(require_admin),
):
    from openpyxl import Workbook

    db = SessionLocal()
    try:
        query = db.query(OperationLog)
        if action:
            actions = [a.strip() for a in action.split(",")]
            if len(actions) == 1:
                query = query.filter(OperationLog.action == actions[0])
            else:
                query = query.filter(OperationLog.action.in_(actions))
        if target_type:
            query = query.filter(OperationLog.target_type == target_type)
        if operator_name:
            query = query.filter(OperationLog.operator_name.contains(operator_name))
        if status:
            query = query.filter(OperationLog.status == status)
        if start_date:
            try:
                sd = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(OperationLog.created_at >= sd)
            except ValueError:
                pass
        if end_date:
            try:
                ed = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
                query = query.filter(OperationLog.created_at <= ed)
            except ValueError:
                pass
        if keyword:
            kw = f"%{keyword}%"
            query = query.filter(
                or_(
                    OperationLog.detail.like(kw),
                    OperationLog.path.like(kw),
                    OperationLog.action.like(kw),
                )
            )

        logs = query.order_by(OperationLog.id.desc()).limit(10000).all()

        wb = Workbook()
        ws = wb.active
        ws.title = "操作日志"
        ws.append(["ID", "操作人ID", "操作人", "操作类型", "操作对象", "对象ID", "详情", "IP地址", "方法", "路径", "状态", "耗时(ms)", "时间"])

        for log in logs:
            ws.append([
                log.id,
                log.operator_id,
                log.operator_name,
                log.action,
                log.target_type,
                log.target_id,
                log.detail,
                log.ip_address,
                log.method,
                log.path,
                log.status,
                log.duration_ms,
                log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else "",
            ])

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        return StreamingResponse(
            output,
            media_type="application/octet-stream",
            headers={"Content-Disposition": "attachment; filename=operation_logs.xlsx"},
        )
    finally:
        db.close()


@router.get("/logs/actions", summary="获取所有操作类型列表")
def get_log_actions(admin_id: int = Depends(require_admin)):
    db = SessionLocal()
    try:
        actions = db.query(OperationLog.action).distinct().all()
        target_types = db.query(OperationLog.target_type).distinct().all()
        return {
            "code": 200,
            "message": "success",
            "data": {
                "actions": sorted([a[0] for a in actions if a[0]]),
                "target_types": sorted([t[0] for t in target_types if t[0]]),
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


@router.get("/users/{user_id}/bills", summary="获取用户账单列表")
def get_user_bills(
    user_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    type: Optional[int] = Query(None, ge=1, le=3, description="类型"),
    admin_id: int = Depends(require_admin),
):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        query = db.query(Bill).join(Account, Bill.account_id == Account.id).filter(Account.user_id == user_id)
        if start_date:
            query = query.filter(Bill.bill_date >= start_date)
        if end_date:
            query = query.filter(Bill.bill_date <= end_date)
        if type is not None:
            query = query.filter(Bill.type == type)

        total = query.count()
        total_income = query.filter(Bill.type == 2).with_entities(func.sum(Bill.amount)).scalar() or 0
        total_expense = query.filter(Bill.type == 1).with_entities(func.sum(Bill.amount)).scalar() or 0

        bills = query.order_by(Bill.bill_date.desc()).offset((page - 1) * size).limit(size).all()

        type_map = {1: "支出", 2: "收入", 3: "转账"}
        items = []
        for b in bills:
            items.append({
                "id": b.id,
                "type": b.type,
                "type_name": type_map.get(b.type, "未知"),
                "amount": b.amount,
                "category_name": b.category.name if b.category else "",
                "category_icon": b.category.icon if b.category else "",
                "account_name": b.account.name if b.account else "",
                "bill_date": str(b.bill_date),
                "remark": b.remark or "",
                "created_at": b.created_at.isoformat() if b.created_at else None,
            })

        return {
            "code": 200,
            "message": "success",
            "data": {
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "total_income": float(total_income),
                "total_expense": float(total_expense),
                "username": user.username,
                "nickname": user.nickname or user.username,
            },
        }
    finally:
        db.close()


@router.get("/users/{user_id}/bills/export", summary="导出用户账单")
def export_user_bills(
    user_id: int,
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    admin_id: int = Depends(require_admin),
):
    import io
    import json
    from openpyxl import Workbook

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        query = db.query(Bill).join(Account, Bill.account_id == Account.id).filter(Account.user_id == user_id)
        if start_date:
            query = query.filter(Bill.bill_date >= start_date)
        if end_date:
            query = query.filter(Bill.bill_date <= end_date)

        bills = query.order_by(Bill.bill_date.desc()).all()
        type_map = {1: "支出", 2: "收入", 3: "转账"}

        wb = Workbook()
        ws = wb.active
        ws.title = "账单"
        ws.append(["日期", "类型", "分类", "账户", "金额", "备注"])

        for b in bills:
            ws.append([
                str(b.bill_date),
                type_map.get(b.type, "未知"),
                b.category.name if b.category else "",
                b.account.name if b.account else "",
                b.amount,
                b.remark or "",
            ])

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        filename = f"user_{user.username}_bills.xlsx"
        return StreamingResponse(
            output,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    finally:
        db.close()
