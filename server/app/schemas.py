"""
Pydantic请求/响应数据模型定义模块。

功能描述：
    定义所有API接口的请求体和响应体数据结构，包括：
    - 统一响应封装 (ApiResponse, PagedApiResponse)
    - 账户相关 (AccountCreate, AccountUpdate, AccountOut)
    - 分类相关 (CategoryCreate, CategoryUpdate, CategoryOut)
    - 标签相关 (TagCreate, TagUpdate, TagOut)
    - 账单相关 (BillCreate, BillUpdate, BillOut)
    - 统计相关 (OverviewOut, CategoryStatOut, TrendItemOut)

使用方法：
    from app.schemas import ApiResponse, BillCreate, BillOut

    @router.post("/bills", response_model=ApiResponse[BillOut])
    def create_bill(bill: BillCreate, db: Session = Depends(get_db)):
        ...

参数说明：
    所有模型字段均使用Python类型注解，Pydantic自动进行数据校验。
    Optional字段表示该参数可选，Field提供默认值和校验规则。

异常处理：
    Pydantic在请求参数校验失败时自动返回422错误，包含详细错误信息。
"""

from datetime import date, datetime, time
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """
    统一API响应格式。

    Attributes:
        code: 状态码 (200=成功, 400=参数错误, 404=未找到, 500=服务器错误)
        message: 响应消息
        data: 响应数据 (泛型)

    示例:
        {"code": 200, "message": "success", "data": {...}}
    """
    code: int = 200
    message: str = "success"
    data: Optional[T] = None


class PagedData(BaseModel, Generic[T]):
    """
    分页数据封装。

    Attributes:
        items: 数据列表
        total: 总记录数
        page: 当前页码
        size: 每页大小
    """
    items: List[T]
    total: int
    page: int
    size: int


# ==================== Account ====================

class AccountCreate(BaseModel):
    """
    创建账户请求体。

    Attributes:
        name: 账户名称 (1-50字符)
        type: 账户类型 (1-现金, 2-银行卡, 3-信用卡, 4-支付宝, 5-微信, 6-其他)
        icon: 图标标识
        color: 颜色标识
        initial_balance: 初始余额 (默认0)
        is_default: 是否设为默认账户 (默认False)
    """
    name: str = Field(..., min_length=1, max_length=50)
    type: int = Field(..., ge=1, le=6)
    icon: str = Field(default="")
    color: str = Field(default="")
    initial_balance: float = Field(default=0)
    is_default: bool = Field(default=False)


class AccountUpdate(BaseModel):
    """
    更新账户请求体。

    所有字段可选，仅更新提供的字段。

    Attributes:
        name: 账户名称
        type: 账户类型
        icon: 图标标识
        color: 颜色标识
        status: 状态 (1-正常, 0-已归档)
    """
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    type: Optional[int] = Field(default=None, ge=1, le=6)
    icon: Optional[str] = None
    color: Optional[str] = None
    status: Optional[int] = Field(default=None, ge=0, le=1)


class AccountOut(BaseModel):
    """
    账户响应体。

    Attributes:
        id: 账户ID
        name: 账户名称
        type: 账户类型
        icon: 图标标识
        color: 颜色标识
        balance: 当前余额
        initial_balance: 初始余额
        is_default: 是否默认账户
        status: 状态
        created_at: 创建时间
        updated_at: 更新时间
    """
    id: int
    name: str
    type: int
    icon: str
    color: str
    balance: float
    initial_balance: float
    is_default: int
    status: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ==================== Category ====================

class CategoryCreate(BaseModel):
    """
    创建分类请求体。

    Attributes:
        parent_id: 父分类ID (None表示顶级分类)
        name: 分类名称 (1-50字符)
        type: 类型 (1-支出, 2-收入)
        icon: 图标标识
    """
    parent_id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=50)
    type: int = Field(..., ge=1, le=2)
    icon: str = Field(default="")


class CategoryUpdate(BaseModel):
    """
    更新分类请求体。

    Attributes:
        name: 分类名称
        icon: 图标标识
    """
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    icon: Optional[str] = None


class CategoryOut(BaseModel):
    """
    分类响应体（含子分类列表）。

    Attributes:
        id: 分类ID
        parent_id: 父分类ID
        name: 分类名称
        type: 类型
        icon: 图标标识
        sort_order: 排序序号
        children: 子分类列表
    """
    id: int
    parent_id: Optional[int]
    name: str
    type: int
    icon: str
    sort_order: int
    children: List["CategoryOut"] = []

    model_config = {"from_attributes": True}


# ==================== Tag ====================

class TagCreate(BaseModel):
    """
    创建标签请求体。

    Attributes:
        name: 标签名称 (1-50字符，唯一)
        color: 颜色标识
    """
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="")


class TagUpdate(BaseModel):
    """
    更新标签请求体。

    Attributes:
        name: 标签名称
        color: 颜色标识
    """
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    color: Optional[str] = None


class TagOut(BaseModel):
    """
    标签响应体。

    Attributes:
        id: 标签ID
        name: 标签名称
        color: 颜色标识
        created_at: 创建时间
    """
    id: int
    name: str
    color: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ==================== Bill ====================

class BillCreate(BaseModel):
    """
    创建账单请求体。

    Attributes:
        account_id: 资金账户ID
        category_id: 分类ID
        type: 类型 (1-支出, 2-收入, 3-转账)
        amount: 金额 (必须大于0)
        bill_date: 账单日期
        bill_time: 账单时间 (可选)
        remark: 备注
        tag_ids: 关联标签ID列表
        transfer_to_account_id: 转入账户ID (仅转账类型需要)
    """
    account_id: int
    category_id: int
    type: int = Field(..., ge=1, le=3)
    amount: float = Field(..., gt=0)
    bill_date: date
    bill_time: Optional[time] = None
    remark: str = Field(default="")
    tag_ids: List[int] = Field(default=[])
    transfer_to_account_id: Optional[int] = None


class BillUpdate(BaseModel):
    """
    更新账单请求体。

    所有字段可选，仅更新提供的字段。

    Attributes:
        account_id: 资金账户ID
        category_id: 分类ID
        type: 类型
        amount: 金额
        bill_date: 账单日期
        bill_time: 账单时间
        remark: 备注
        tag_ids: 关联标签ID列表 (提供时替换全部标签)
        transfer_to_account_id: 转入账户ID
    """
    account_id: Optional[int] = None
    category_id: Optional[int] = None
    type: Optional[int] = Field(default=None, ge=1, le=3)
    amount: Optional[float] = Field(default=None, gt=0)
    bill_date: Optional[date] = None
    bill_time: Optional[time] = None
    remark: Optional[str] = None
    tag_ids: Optional[List[int]] = None
    transfer_to_account_id: Optional[int] = None


class TagBrief(BaseModel):
    """标签简要信息（嵌入账单响应中）。"""
    id: int
    name: str
    color: str

    model_config = {"from_attributes": True}


class BillOut(BaseModel):
    """
    账单响应体。

    Attributes:
        id: 账单ID
        account_id: 资金账户ID
        account_name: 资金账户名称
        category_id: 分类ID
        category_name: 分类名称
        category_icon: 分类图标
        type: 类型
        amount: 金额
        bill_date: 账单日期
        bill_time: 账单时间
        remark: 备注
        tags: 关联标签列表
        transfer_to_account_id: 转入账户ID
        created_at: 创建时间
        updated_at: 更新时间
    """
    id: int
    account_id: int
    account_name: str
    category_id: int
    category_name: str
    category_icon: str
    type: int
    amount: float
    bill_date: date
    bill_time: Optional[time]
    remark: str
    tags: List[TagBrief]
    transfer_to_account_id: Optional[int]
    created_at: datetime
    updated_at: datetime


# ==================== Statistics ====================

class OverviewOut(BaseModel):
    """
    收支概览响应体。

    Attributes:
        total_income: 总收入
        total_expense: 总支出
        balance: 结余 (收入-支出)
        bill_count: 账单总数
    """
    total_income: float
    total_expense: float
    balance: float
    bill_count: int


class CategoryStatOut(BaseModel):
    """
    分类统计响应体。

    Attributes:
        category_id: 分类ID
        category_name: 分类名称
        category_icon: 分类图标
        amount: 该分类总金额
        percentage: 占总金额的百分比
        bill_count: 该分类账单数
    """
    category_id: int
    category_name: str
    category_icon: str
    amount: float
    percentage: float
    bill_count: int


class TrendItemOut(BaseModel):
    """
    趋势分析单项响应体。

    Attributes:
        period: 时间段标识 (如"2026-04")
        income: 该时段收入
        expense: 该时段支出
    """
    period: str
    income: float
    expense: float


class BalanceTrendItemOut(BaseModel):
    """
    余额趋势单项响应体。

    Attributes:
        date: 日期
        balance: 当日余额
        income: 当日收入
        expense: 当日支出
    """
    date: str
    balance: float
    income: float = 0
    expense: float = 0


class AccountBalanceTrendOut(BaseModel):
    """
    账户余额趋势响应体。

    Attributes:
        account_id: 账户ID
        account_name: 账户名称
        account_type: 账户类型
        account_type_name: 账户类型名称
        current_balance: 当前余额
        color: 图表颜色
        data: 余额趋势数据列表
    """
    account_id: int
    account_name: str
    account_type: int
    account_type_name: str
    current_balance: float
    color: str
    data: List[BalanceTrendItemOut]
