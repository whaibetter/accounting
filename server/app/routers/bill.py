"""
账单API路由模块。

功能描述：
    提供账单的增删改查接口，支持：
    - 获取账单列表（分页+多条件筛选）
    - 创建新账单（自动更新账户余额）
    - 获取单个账单详情
    - 更新账单信息（自动调整账户余额）
    - 删除账单（自动回滚账户余额）

接口列表：
    GET    /api/v1/bills          获取账单列表
    POST   /api/v1/bills          创建账单
    GET    /api/v1/bills/{id}     获取账单详情
    PUT    /api/v1/bills/{id}     更新账单
    DELETE /api/v1/bills/{id}     删除账单

余额变动规则：
    - 支出(type=1): 从账户扣减金额
    - 收入(type=2): 向账户增加金额
    - 转账(type=3): 从源账户扣减，向目标账户增加

异常处理：
    - 404: 账单不存在
    - 400: 关联资源不存在（账户、分类、标签）
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.database import get_db
from app import crud, schemas
from app.models import Bill, BillTag

router = APIRouter(prefix="/api/v1/bills", tags=["账单管理"])


def _bill_to_out(bill: Bill) -> schemas.BillOut:
    """
    将Bill ORM对象转换为BillOut响应模型。

    Args:
        bill: Bill ORM对象

    Returns:
        BillOut: 包含账户名称、分类名称、标签列表的完整账单响应
    """
    tags = [
        schemas.TagBrief(id=link.tag.id, name=link.tag.name, color=link.tag.color)
        for link in bill.tag_links
    ]
    return schemas.BillOut(
        id=bill.id,
        account_id=bill.account_id,
        account_name=bill.account.name if bill.account else "",
        category_id=bill.category_id,
        category_name=bill.category.name if bill.category else "",
        category_icon=bill.category.icon if bill.category else "",
        type=bill.type,
        amount=bill.amount,
        bill_date=bill.bill_date,
        bill_time=bill.bill_time,
        remark=bill.remark,
        tags=tags,
        transfer_to_account_id=bill.transfer_to_account_id,
        created_at=bill.created_at,
        updated_at=bill.updated_at,
    )


@router.get("", response_model=schemas.ApiResponse[schemas.PagedData[schemas.BillOut]],
            summary="获取账单列表")
def list_bills(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    type: Optional[int] = Query(None, ge=1, le=3, description="类型: 1-支出 2-收入 3-转账"),
    category_id: Optional[int] = Query(None, description="分类ID"),
    account_id: Optional[int] = Query(None, description="账户ID"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    db: Session = Depends(get_db),
):
    """
    获取账单列表，支持分页和多条件筛选。

    筛选条件可组合使用，不传则不筛选。

    Args:
        page: 页码 (从1开始)
        size: 每页大小 (1-100)
        start_date: 开始日期筛选
        end_date: 结束日期筛选
        type: 类型筛选
        category_id: 分类ID筛选
        account_id: 账户ID筛选
        keyword: 关键词搜索 (匹配备注)

    Returns:
        ApiResponse[PagedData[BillOut]]: 分页账单列表
    """
    result = crud.get_bills(
        db, page=page, size=size, start_date=start_date, end_date=end_date,
        type_=type, category_id=category_id, account_id=account_id, keyword=keyword,
    )
    items = [_bill_to_out(b) for b in result["items"]]
    paged = schemas.PagedData(items=items, total=result["total"],
                              page=result["page"], size=result["size"])
    return schemas.ApiResponse(data=paged)


@router.post("", response_model=schemas.ApiResponse[schemas.BillOut],
             summary="创建账单")
def create_bill(bill: schemas.BillCreate, db: Session = Depends(get_db)):
    """
    创建新账单。

    创建时自动更新关联账户的余额。

    Args:
        bill: 账单创建请求体

    Returns:
        ApiResponse[BillOut]: 新创建的账单信息

    Raises:
        HTTPException 400: 关联资源不存在
    """
    try:
        new_bill = crud.create_bill(
            db, account_id=bill.account_id, category_id=bill.category_id,
            type_=bill.type, amount=bill.amount, bill_date=bill.bill_date,
            bill_time=bill.bill_time, remark=bill.remark,
            tag_ids=bill.tag_ids, transfer_to_account_id=bill.transfer_to_account_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return schemas.ApiResponse(data=_bill_to_out(new_bill))


@router.get("/{bill_id}", response_model=schemas.ApiResponse[schemas.BillOut],
            summary="获取账单详情")
def get_bill(bill_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取单个账单的详细信息。

    Args:
        bill_id: 账单ID

    Returns:
        ApiResponse[BillOut]: 账单详情

    Raises:
        HTTPException 404: 账单不存在
    """
    bill = crud.get_bill(db, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="账单不存在")
    return schemas.ApiResponse(data=_bill_to_out(bill))


@router.put("/{bill_id}", response_model=schemas.ApiResponse[schemas.BillOut],
            summary="更新账单")
def update_bill(bill_id: int, bill: schemas.BillUpdate, db: Session = Depends(get_db)):
    """
    更新账单信息。

    更新时自动调整账户余额变动（先撤销旧账单影响，再应用新账单影响）。

    Args:
        bill_id: 账单ID
        bill: 账单更新请求体

    Returns:
        ApiResponse[BillOut]: 更新后的账单信息

    Raises:
        HTTPException 404: 账单不存在
    """
    update_data = bill.model_dump(exclude_none=True)
    updated = crud.update_bill(db, bill_id, **update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="账单不存在")
    return schemas.ApiResponse(data=_bill_to_out(updated))


@router.delete("/{bill_id}", response_model=schemas.ApiResponse[None],
               summary="删除账单")
def delete_bill(bill_id: int, db: Session = Depends(get_db)):
    """
    删除账单。

    删除时自动回滚对账户余额的影响。

    Args:
        bill_id: 账单ID

    Returns:
        ApiResponse[None]: 删除结果

    Raises:
        HTTPException 404: 账单不存在
    """
    if not crud.delete_bill(db, bill_id):
        raise HTTPException(status_code=404, detail="账单不存在")
    return schemas.ApiResponse(message="删除成功")
