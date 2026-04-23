"""
数据导入API路由模块。

功能描述：
    提供JSON格式数据的批量导入接口，支持：
    - 批量导入账户（根据名称去重，已存在跳过）
    - 批量导入账单（自动匹配账户名称和分类名称）
    - 预览解析结果

接口列表：
    POST /api/v1/import/accounts   批量导入账户
    POST /api/v1/import/bills      批量导入账单

导入规则：
    - 账户：根据 name 字段去重，name 相同则跳过
    - 账单：自动根据 account 字段匹配已有账户，根据 category 匹配已有分类
    - 分类支持模糊匹配（如"午餐"匹配"午餐"子分类）
    - 日期支持 YYYY-MM-DD 或 YYYY/MM/DD 格式
    - type: 1=支出, 2=收入
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from app.database import get_db
from app import crud

router = APIRouter(prefix="/api/v1/import", tags=["数据导入"])


class AccountImportItem(BaseModel):
    name: str = Field(..., description="账户名称")
    type: Optional[int] = Field(1, ge=1, le=6, description="账户类型: 1-现金 2-银行卡 3-信用卡 4-支付宝 5-微信 6-其他")
    icon: Optional[str] = Field("", description="图标标识")
    color: Optional[str] = Field("", description="颜色标识")
    initial_balance: Optional[float] = Field(0, description="初始余额")


class AccountImportRequest(BaseModel):
    accounts: List[AccountImportItem] = Field(..., description="账户列表")


class BillImportItem(BaseModel):
    account: str = Field(..., description="账户名称（必须已存在）")
    category: Optional[str] = Field(None, description="分类名称（支持模糊匹配）")
    type: Optional[int] = Field(1, ge=1, le=2, description="类型: 1-支出 2-收入")
    amount: float = Field(..., gt=0, description="金额（必须大于0）")
    date: Optional[str] = Field(None, description="账单日期 YYYY-MM-DD 或 YYYY/MM/DD")
    bill_date: Optional[str] = Field(None, description="账单日期（date的别名）")
    time: Optional[str] = Field(None, description="账单时间 HH:MM")
    bill_time: Optional[str] = Field(None, description="账单时间（time的别名）")
    remark: Optional[str] = Field("", description="备注")
    tag_ids: Optional[List[int]] = Field(default_factory=list, description="标签ID列表")


class BillImportRequest(BaseModel):
    bills: List[BillImportItem] = Field(..., description="账单列表")


@router.post("/accounts", summary="批量导入账户")
def import_accounts(req: AccountImportRequest, db=Depends(get_db)):
    """
    批量导入资金账户。

    根据账户名称去重，已存在的账户会跳过。
    账户余额初始化为 initial_balance。

    请求示例:
    ```json
    {
      "accounts": [
        {"Name": "建设银行储蓄卡", "type": 2, "initial_balance": 10000},
        {"Name": "支付宝", "type": 4, "initial_balance": 5000}
      ]
    }
    ```

    Returns:
        success: 成功导入数量
        skipped: 跳过的数量（已存在）
        errors: 错误信息列表
    """
    raw_data = [a.model_dump() for a in req.accounts]
    result = crud.import_accounts_batch(db, raw_data)
    return {"code": 200, "message": "导入完成", "data": result}


@router.post("/bills", summary="批量导入账单")
def import_bills(req: BillImportRequest, db=Depends(get_db)):
    """
    批量导入账单。

    自动根据 account 字段匹配已有账户，根据 category 匹配已有分类。
    导入时自动更新账户余额。

    请求示例:
    ```json
    {
      "bills": [
        {"account": "建设银行储蓄卡", "category": "午餐", "type": 1, "amount": 35.5, "date": "2026-04-17", "remark": "工作餐"},
        {"account": "支付宝", "category": "打车", "type": 1, "amount": 28.0, "date": "2026-04-17"},
        {"account": "建设银行储蓄卡", "category": "工资", "type": 2, "amount": 15000, "date": "2026-04-01"}
      ]
    }
    ```

    Returns:
        success: 成功导入数量
        errors: 错误信息列表（含原始数据和失败原因）
    """
    accounts = crud.get_accounts(db)
    account_map = {acc.name: acc.id for acc in accounts}

    if not account_map:
        raise HTTPException(status_code=400, detail="请先创建账户后再导入账单")

    raw_data = [b.model_dump() for b in req.bills]
    result = crud.import_bills_batch(db, raw_data, account_map)
    return {"code": 200, "message": "导入完成", "data": result}
