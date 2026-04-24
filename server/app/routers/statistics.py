"""
统计分析API路由模块。

功能描述：
    提供财务数据统计分析接口，支持：
    - 收支概览（总收入、总支出、结余）
    - 分类统计（各分类金额占比）
    - 收支趋势（按月/按日趋势）

接口列表：
    GET /api/v1/statistics/overview       收支概览
    GET /api/v1/statistics/by-category    分类统计
    GET /api/v1/statistics/trend          收支趋势

统计规则：
    - 支出统计包含类型1(支出)和类型3(转账)的金额
    - 收入统计仅包含类型2(收入)的金额
    - 分类统计仅统计顶级分类，子分类金额汇总到父分类
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/api/v1/statistics", tags=["统计分析"])


@router.get("/overview", response_model=schemas.ApiResponse[schemas.OverviewOut],
            summary="收支概览")
def get_overview(
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
):
    """
    获取收支概览数据。

    返回指定时间范围内的总收入、总支出、结余和账单数。
    不传日期参数则统计全部数据。

    Args:
        start_date: 开始日期 (可选)
        end_date: 结束日期 (可选)

    Returns:
        ApiResponse[OverviewOut]: 收支概览数据

    示例:
        GET /api/v1/statistics/overview?start_date=2026-04-01&end_date=2026-04-30
    """
    data = crud.get_overview(db, start_date=start_date, end_date=end_date)
    return schemas.ApiResponse(data=schemas.OverviewOut(**data))


@router.get("/by-category", response_model=schemas.ApiResponse[list[schemas.CategoryStatOut]],
            summary="分类统计")
def get_category_stats(
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    type: int = Query(1, ge=1, le=2, description="类型: 1-支出 2-收入"),
    db: Session = Depends(get_db),
):
    """
    获取分类统计数据。

    返回各顶级分类的金额和占比，按金额降序排列。
    子分类的金额汇总到其父分类。

    Args:
        start_date: 开始日期 (可选)
        end_date: 结束日期 (可选)
        type: 类型筛选 (1-支出, 2-收入，默认支出)

    Returns:
        ApiResponse[List[CategoryStatOut]]: 分类统计列表

    示例:
        GET /api/v1/statistics/by-category?start_date=2026-04-01&end_date=2026-04-30&type=1
    """
    data = crud.get_category_stats(db, start_date=start_date, end_date=end_date, type_=type)
    return schemas.ApiResponse(data=[schemas.CategoryStatOut(**d) for d in data])


@router.get("/trend", response_model=schemas.ApiResponse[list[schemas.TrendItemOut]],
            summary="收支趋势")
def get_trend(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    granularity: str = Query("month", pattern="^(month|day)$", description="粒度: month-按月 day-按日"),
    db: Session = Depends(get_db),
):
    """
    获取收支趋势数据。

    返回指定时间范围内按月或按日的收入和支出金额。

    Args:
        start_date: 开始日期 (必填)
        end_date: 结束日期 (必填)
        granularity: 统计粒度 ("month" 或 "day"，默认"month")

    Returns:
        ApiResponse[List[TrendItemOut]]: 趋势数据列表

    示例:
        GET /api/v1/statistics/trend?start_date=2026-01-01&end_date=2026-04-30&granularity=month
    """
    data = crud.get_trend(db, start_date=start_date, end_date=end_date, granularity=granularity)
    return schemas.ApiResponse(data=[schemas.TrendItemOut(**d) for d in data])


@router.get("/balance-trend", response_model=schemas.ApiResponse[list[schemas.AccountBalanceTrendOut]],
            summary="账户余额趋势")
def get_balance_trend(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    account_id: Optional[int] = Query(None, description="账户ID (不传则返回所有账户)"),
    account_type: Optional[int] = Query(None, ge=1, le=6, description="账户类型: 1-现金 2-银行卡 3-信用卡 4-支付宝 5-微信 6-其他"),
    db: Session = Depends(get_db),
):
    """
    获取账户余额趋势数据。

    返回指定时间范围内每个账户每天的余额变化曲线。
    支持按账户ID和账户类型筛选。

    Args:
        start_date: 开始日期 (必填)
        end_date: 结束日期 (必填)
        account_id: 账户ID (可选)
        account_type: 账户类型 (可选, 1-现金 2-银行卡 3-信用卡 4-支付宝 5-微信 6-其他)

    Returns:
        ApiResponse[List[AccountBalanceTrendOut]]: 账户余额趋势列表

    示例:
        GET /api/v1/statistics/balance-trend?start_date=2026-01-01&end_date=2026-04-30
        GET /api/v1/statistics/balance-trend?start_date=2026-01-01&end_date=2026-04-30&account_type=2
        GET /api/v1/statistics/balance-trend?start_date=2026-01-01&end_date=2026-04-30&account_id=1
    """
    data = crud.get_balance_trend(db, start_date=start_date, end_date=end_date,
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
