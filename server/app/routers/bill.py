from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.database import get_db
from app import crud, schemas
from app.models import Bill, BillTag
from app.dependencies import require_auth

router = APIRouter(prefix="/api/v1/bills", tags=["账单管理"], dependencies=[Depends(require_auth)])


def _bill_to_out(bill: Bill) -> schemas.BillOut:
    tags = [
        schemas.TagBrief(id=link.tag.id, name=link.tag.name, icon=link.tag.icon or "", color=link.tag.color)
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
    user_id: int = Depends(require_auth),
    db: Session = Depends(get_db),
):
    result = crud.get_bills(
        db, user_id, page=page, size=size, start_date=start_date, end_date=end_date,
        type_=type, category_id=category_id, account_id=account_id, keyword=keyword,
    )
    items = [_bill_to_out(b) for b in result["items"]]
    paged = schemas.PagedData(items=items, total=result["total"],
                              page=result["page"], size=result["size"])
    return schemas.ApiResponse(data=paged)


@router.post("", response_model=schemas.ApiResponse[schemas.BillOut],
             summary="创建账单")
def create_bill(bill: schemas.BillCreate, user_id: int = Depends(require_auth), db: Session = Depends(get_db)):
    try:
        new_bill = crud.create_bill(
            db, user_id, account_id=bill.account_id, category_id=bill.category_id,
            type_=bill.type, amount=bill.amount, bill_date=bill.bill_date,
            bill_time=bill.bill_time, remark=bill.remark,
            tag_ids=bill.tag_ids, transfer_to_account_id=bill.transfer_to_account_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return schemas.ApiResponse(data=_bill_to_out(new_bill))


@router.get("/{bill_id}", response_model=schemas.ApiResponse[schemas.BillOut],
            summary="获取账单详情")
def get_bill(bill_id: int, user_id: int = Depends(require_auth), db: Session = Depends(get_db)):
    bill = crud.get_bill(db, bill_id, user_id)
    if not bill:
        raise HTTPException(status_code=404, detail="账单不存在")
    return schemas.ApiResponse(data=_bill_to_out(bill))


@router.put("/{bill_id}", response_model=schemas.ApiResponse[schemas.BillOut],
            summary="更新账单")
def update_bill(bill_id: int, bill: schemas.BillUpdate, user_id: int = Depends(require_auth), db: Session = Depends(get_db)):
    update_data = bill.model_dump(exclude_none=True)
    updated = crud.update_bill(db, bill_id, user_id, **update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="账单不存在")
    return schemas.ApiResponse(data=_bill_to_out(updated))


@router.delete("/{bill_id}", response_model=schemas.ApiResponse[None],
               summary="删除账单")
def delete_bill(bill_id: int, user_id: int = Depends(require_auth), db: Session = Depends(get_db)):
    if not crud.delete_bill(db, bill_id, user_id):
        raise HTTPException(status_code=404, detail="账单不存在")
    return schemas.ApiResponse(message="删除成功")
