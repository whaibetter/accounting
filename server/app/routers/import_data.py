from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from app.database import get_db
from app import crud
from app.dependencies import require_auth

router = APIRouter(prefix="/api/v1/import", tags=["数据导入"], dependencies=[Depends(require_auth)])


class AccountImportItem(BaseModel):
    name: str = Field(..., description="账户名称")
    type: Optional[int] = Field(1, ge=1, le=6, description="账户类型")
    icon: Optional[str] = Field("", description="图标标识")
    color: Optional[str] = Field("", description="颜色标识")
    initial_balance: Optional[float] = Field(0, description="初始余额")


class AccountImportRequest(BaseModel):
    accounts: List[AccountImportItem] = Field(..., description="账户列表")


class BillImportItem(BaseModel):
    account: str = Field(..., description="账户名称")
    category: Optional[str] = Field(None, description="分类名称")
    type: Optional[int] = Field(1, ge=1, le=2, description="类型: 1-支出 2-收入")
    amount: float = Field(..., gt=0, description="金额")
    date: Optional[str] = Field(None, description="账单日期")
    bill_date: Optional[str] = Field(None, description="账单日期别名")
    time: Optional[str] = Field(None, description="账单时间")
    bill_time: Optional[str] = Field(None, description="账单时间别名")
    remark: Optional[str] = Field("", description="备注")
    tag_ids: Optional[List[int]] = Field(default_factory=list, description="标签ID列表")


class BillImportRequest(BaseModel):
    bills: List[BillImportItem] = Field(..., description="账单列表")


@router.post("/accounts", summary="批量导入账户")
def import_accounts(req: AccountImportRequest, user_id: int = Depends(require_auth), db=Depends(get_db)):
    raw_data = [a.model_dump() for a in req.accounts]
    result = crud.import_accounts_batch(db, user_id, raw_data)
    return {"code": 200, "message": "导入完成", "data": result}


@router.post("/bills", summary="批量导入账单")
def import_bills(req: BillImportRequest, user_id: int = Depends(require_auth), db=Depends(get_db)):
    accounts = crud.get_accounts(db, user_id)
    account_map = {acc.name: acc.id for acc in accounts}

    if not account_map:
        raise HTTPException(status_code=400, detail="请先创建账户后再导入账单")

    raw_data = [b.model_dump() for b in req.bills]
    result = crud.import_bills_batch(db, user_id, raw_data, account_map)
    return {"code": 200, "message": "导入完成", "data": result}
