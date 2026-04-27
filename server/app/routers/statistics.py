from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.database import get_db
from app import crud, schemas
from app.dependencies import require_auth

router = APIRouter(prefix="/api/v1/statistics", tags=["统计分析"], dependencies=[Depends(require_auth)])


@router.get("/overview", response_model=schemas.ApiResponse[schemas.OverviewOut],
            summary="收支概览")
def get_overview(
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    user_id: int = Depends(require_auth),
    db: Session = Depends(get_db),
):
    data = crud.get_overview(db, user_id, start_date=start_date, end_date=end_date)
    return schemas.ApiResponse(data=schemas.OverviewOut(**data))


@router.get("/by-category", response_model=schemas.ApiResponse[list[schemas.CategoryStatOut]],
            summary="分类统计")
def get_category_stats(
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    type: int = Query(1, ge=1, le=2, description="类型: 1-支出 2-收入"),
    user_id: int = Depends(require_auth),
    db: Session = Depends(get_db),
):
    data = crud.get_category_stats(db, user_id, start_date=start_date, end_date=end_date, type_=type)
    return schemas.ApiResponse(data=[schemas.CategoryStatOut(**d) for d in data])


@router.get("/trend", response_model=schemas.ApiResponse[list[schemas.TrendItemOut]],
            summary="收支趋势")
def get_trend(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    granularity: str = Query("month", pattern="^(month|day)$", description="粒度: month-按月 day-按日"),
    user_id: int = Depends(require_auth),
    db: Session = Depends(get_db),
):
    data = crud.get_trend(db, user_id, start_date=start_date, end_date=end_date, granularity=granularity)
    return schemas.ApiResponse(data=[schemas.TrendItemOut(**d) for d in data])


@router.get("/balance-trend", response_model=schemas.ApiResponse[list[schemas.AccountBalanceTrendOut]],
            summary="账户余额趋势")
def get_balance_trend(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    account_id: Optional[int] = Query(None, description="账户ID"),
    account_type: Optional[int] = Query(None, ge=1, le=6, description="账户类型"),
    user_id: int = Depends(require_auth),
    db: Session = Depends(get_db),
):
    data = crud.get_balance_trend(db, user_id, start_date=start_date, end_date=end_date,
                                  account_id=account_id, account_type=account_type)
    return schemas.ApiResponse(data=[schemas.AccountBalanceTrendOut(
        account_id=d["account_id"],
        account_name=d["account_name"],
        account_type=d["account_type"],
        account_type_name=d["account_type_name"],
        current_balance=d["current_balance"],
        color=d["color"],
        data=[schemas.BalanceTrendItemOut(**item) for item in d["data"]]
    ) for d in data])
