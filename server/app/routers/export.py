import io
import json
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud
from app.dependencies import require_auth

router = APIRouter(prefix="/api/v1/export", tags=["数据导出"], dependencies=[Depends(require_auth)])


@router.get("/excel", summary="导出Excel")
def export_excel(
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    user_id: int = Depends(require_auth),
    db: Session = Depends(get_db),
):
    result = crud.get_bills(db, user_id, page=1, size=99999,
                            start_date=start_date, end_date=end_date)
    bills = result["items"]

    wb = Workbook()
    ws = wb.active
    ws.title = "账单"

    headers = ["日期", "时间", "类型", "分类", "账户", "金额", "备注", "标签"]
    ws.append(headers)

    type_map = {1: "支出", 2: "收入", 3: "转账"}

    for bill in bills:
        tag_names = ",".join([link.tag.name for link in bill.tag_links])
        ws.append([
            str(bill.bill_date),
            str(bill.bill_time) if bill.bill_time else "",
            type_map.get(bill.type, "未知"),
            bill.category.name if bill.category else "",
            bill.account.name if bill.account else "",
            bill.amount,
            bill.remark,
            tag_names,
        ])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"accounting_{start_date or 'all'}_{end_date or 'all'}.xlsx"
    return StreamingResponse(
        output,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/json", summary="导出JSON")
def export_json(
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    user_id: int = Depends(require_auth),
    db: Session = Depends(get_db),
):
    result = crud.get_bills(db, user_id, page=1, size=99999,
                            start_date=start_date, end_date=end_date)
    bills = result["items"]

    type_map = {1: "支出", 2: "收入", 3: "转账"}
    data = []
    for bill in bills:
        data.append({
            "id": bill.id,
            "date": str(bill.bill_date),
            "time": str(bill.bill_time) if bill.bill_time else None,
            "type": type_map.get(bill.type, "未知"),
            "category": bill.category.name if bill.category else "",
            "account": bill.account.name if bill.account else "",
            "amount": bill.amount,
            "remark": bill.remark,
            "tags": [link.tag.name for link in bill.tag_links],
            "created_at": str(bill.created_at),
        })

    output = io.BytesIO(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
    output.seek(0)

    filename = f"accounting_{start_date or 'all'}_{end_date or 'all'}.json"
    return StreamingResponse(
        output,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
