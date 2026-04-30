from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Date, Time, ForeignKey, UniqueConstraint, Text
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(200), nullable=False)
    nickname = Column(String(50), default="")
    avatar = Column(String(200), default="")
    email = Column(String(100), default="")
    phone = Column(String(20), default="")
    is_admin = Column(Integer, nullable=False, default=0)
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    accounts = relationship("Account", back_populates="user", foreign_keys="Account.user_id")
    categories = relationship("Category", back_populates="user", foreign_keys="Category.user_id")
    tags = relationship("Tag", back_populates="user", foreign_keys="Tag.user_id")


class SystemConfig(Base):
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), nullable=False, unique=True)
    value = Column(String(500), nullable=False, default="")
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
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

    user = relationship("User", back_populates="accounts")
    bills = relationship("Bill", back_populates="account", foreign_keys="Bill.account_id")


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("category.id"), default=None)
    name = Column(String(50), nullable=False)
    type = Column(Integer, nullable=False)
    icon = Column(String(50), default="")
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    user = relationship("User", back_populates="categories")
    parent = relationship("Category", remote_side=[id], backref="children")
    bills = relationship("Bill", back_populates="category")


class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    icon = Column(String(50), default="")
    color = Column(String(20), default="")
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    user = relationship("User", back_populates="tags")


class Bill(Base):
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
    __tablename__ = "bill_tag"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bill_id = Column(Integer, ForeignKey("bill.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tag.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("bill_id", "tag_id", name="uq_bill_tag"),
    )

    bill = relationship("Bill", back_populates="tag_links")
    tag = relationship("Tag")


class OperationLog(Base):
    __tablename__ = "operation_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    operator_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    operator_name = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False, index=True)
    target_type = Column(String(50), default="")
    target_id = Column(Integer, default=None)
    detail = Column(String(500), default="")
    ip_address = Column(String(50), default="")
    method = Column(String(10), default="")
    path = Column(String(200), default="")
    status = Column(String(20), default="success")
    duration_ms = Column(Integer, default=None)
    extra_data = Column(Text, default=None)
    created_at = Column(DateTime, nullable=False, default=datetime.now, index=True)

    operator = relationship("User")
