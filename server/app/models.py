"""
SQLAlchemy数据模型定义模块。

功能描述：
    定义所有数据库表对应的ORM模型，包括：
    - Account: 资金账户表
    - Category: 分类表（支持二级分类）
    - Tag: 标签表
    - Bill: 账单表
    - BillTag: 账单-标签关联表

使用方法：
    from app.models import Account, Category, Tag, Bill, BillTag

关系说明：
    Account 1:N Bill        一个账户有多笔账单
    Category 1:N Bill       一个分类有多笔账单
    Category 自关联          分类支持父子二级结构
    Bill N:M Tag            账单与标签多对多，通过BillTag关联
"""

from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Date, Time, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.database import Base


class SystemConfig(Base):
    """
    系统配置模型。

    存储系统级配置信息，如密码哈希、JWT密钥等。
    采用键值对结构，支持灵活扩展。

    Attributes:
        id: 主键，自增
        key: 配置键名（唯一）
        value: 配置值
        updated_at: 更新时间
    """
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), nullable=False, unique=True)
    value = Column(String(500), nullable=False, default="")
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class Account(Base):
    """
    资金账户模型。

    管理用户的各类资金账户，如现金、银行卡、信用卡、支付宝、微信等。
    每个账户跟踪当前余额和初始余额。

    Attributes:
        id: 主键，自增
        name: 账户名称，如"招商银行储蓄卡"
        type: 账户类型 (1-现金, 2-银行卡, 3-信用卡, 4-支付宝, 5-微信, 6-其他)
        icon: 图标标识
        color: 颜色标识 (十六进制色值)
        balance: 当前余额
        initial_balance: 初始余额
        sort_order: 排序序号
        is_default: 是否默认账户 (0-否, 1-是)
        status: 状态 (1-正常, 0-已归档)
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    type = Column(Integer, nullable=False, default=1)
    icon = Column(String(50), default="")
    color = Column(String(20), default="")
    balance = Column(Float, nullable=False, default=0)
    initial_balance = Column(Float, nullable=False, default=0)
    sort_order = Column(Integer, nullable=False, default=0)
    is_default = Column(Integer, nullable=False, default=0)
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    bills = relationship("Bill", back_populates="account", foreign_keys="Bill.account_id")


class Category(Base):
    """
    分类模型。

    支持二级分类结构，通过parent_id自关联实现。
    顶级分类的parent_id为None，子分类的parent_id指向父分类。

    Attributes:
        id: 主键，自增
        parent_id: 父分类ID (None表示顶级分类)
        name: 分类名称
        type: 类型 (1-支出, 2-收入)
        icon: 图标标识
        sort_order: 排序序号
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("category.id"), default=None)
    name = Column(String(50), nullable=False)
    type = Column(Integer, nullable=False)
    icon = Column(String(50), default="")
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    parent = relationship("Category", remote_side=[id], backref="children")
    bills = relationship("Bill", back_populates="category")


class Tag(Base):
    """
    标签模型。

    标签用于对账单进行多维度标记，与账单为多对多关系。

    Attributes:
        id: 主键，自增
        name: 标签名称 (唯一)
        color: 颜色标识
        created_at: 创建时间
    """
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    color = Column(String(20), default="")
    created_at = Column(DateTime, nullable=False, default=datetime.now)


class Bill(Base):
    """
    账单模型。

    记录每一笔收支和转账操作。
    支出/收入时关联account_id，转账时额外关联transfer_to_account_id。

    Attributes:
        id: 主键，自增
        account_id: 资金账户ID (外键)
        category_id: 分类ID (外键)
        type: 类型 (1-支出, 2-收入, 3-转账)
        amount: 金额 (绝对值)
        bill_date: 账单日期
        bill_time: 账单时间 (可空)
        remark: 备注
        transfer_to_account_id: 转入账户ID (仅转账类型)
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "bill"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("account.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    type = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    bill_date = Column(Date, nullable=False)
    bill_time = Column(Time, default=None)
    remark = Column(String(500), default="")
    transfer_to_account_id = Column(Integer, ForeignKey("account.id"), default=None)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    account = relationship("Account", back_populates="bills", foreign_keys=[account_id])
    category = relationship("Category", back_populates="bills")
    transfer_to_account = relationship("Account", foreign_keys=[transfer_to_account_id])
    tag_links = relationship("BillTag", back_populates="bill", cascade="all, delete-orphan")


class BillTag(Base):
    """
    账单-标签关联模型。

    实现账单与标签的多对多关系。
    同一账单不能重复关联同一标签。

    Attributes:
        id: 主键，自增
        bill_id: 账单ID (外键)
        tag_id: 标签ID (外键)
    """
    __tablename__ = "bill_tag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bill_id = Column(Integer, ForeignKey("bill.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tag.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("bill_id", "tag_id", name="uq_bill_tag"),
    )

    bill = relationship("Bill", back_populates="tag_links")
    tag = relationship("Tag")
