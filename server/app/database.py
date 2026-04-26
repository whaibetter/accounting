"""
数据库连接配置与会话管理模块。

功能描述：
    - 配置SQLite数据库连接
    - 提供数据库会话的依赖注入
    - 管理数据库表的创建与预设数据的初始化

使用方法：
    from app.database import get_db, engine, Base

    # 在路由中通过依赖注入获取数据库会话
    @router.get("/items")
    def list_items(db: Session = Depends(get_db)):
        ...

参数说明：
    DATABASE_URL: SQLite数据库文件路径，默认为 data/accounting.db

异常处理：
    - 数据库文件目录不存在时自动创建
    - 首次启动时自动执行表创建和预设数据初始化
"""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{DATA_DIR / 'accounting.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """
    获取数据库会话的依赖注入函数。

    Yields:
        Session: SQLAlchemy数据库会话对象

    使用示例：
        @router.get("/accounts")
        def list_accounts(db: Session = Depends(get_db)):
            return crud.get_accounts(db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库。

    执行以下操作：
        1. 创建所有数据表（如果不存在）
        2. 插入预设分类数据（如果分类表为空）
        3. 初始化认证系统（密码哈希、JWT密钥）

    此函数应在应用启动时调用一次。
    """
    from app.models import Account, Category, SystemConfig  # noqa: F401
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        _seed_categories(db)
        _seed_default_account(db)
    finally:
        db.close()

    from app.auth import init_auth
    init_auth()


def _seed_categories(db):
    """
    插入预设分类数据。

    当分类表为空时，插入系统预设的支出和收入分类。
    分类采用二级结构：大类 → 子分类。

    Args:
        db: SQLAlchemy数据库会话
    """
    from app.models import Category as CatModel
    if db.query(CatModel).first() is not None:
        return

    expense_categories = [
        ("餐饮", "food", ["早餐", "午餐", "晚餐", "零食", "饮料"]),
        ("交通", "transport", ["公交", "地铁", "打车", "加油", "停车"]),
        ("购物", "shopping", ["日用品", "衣物", "数码", "美妆"]),
        ("居住", "housing", ["房租", "水电", "物业", "网费"]),
        ("娱乐", "entertainment", ["电影", "游戏", "旅行", "运动"]),
        ("医疗", "medical", ["门诊", "药品", "体检"]),
        ("教育", "education", ["书籍", "课程", "培训"]),
        ("通讯", "telecom", ["话费", "会员"]),
        ("人情", "social", ["红包", "礼物", "请客"]),
        ("其他", "other_expense", []),
    ]

    income_categories = [
        ("工资", "salary", []),
        ("兼职", "parttime", []),
        ("理财", "investment", []),
        ("红包", "redpacket", []),
        ("退款", "refund", []),
        ("其他", "other_income", []),
    ]

    sort = 0
    for name, icon, children in expense_categories:
        parent = CatModel(
            name=name, type=1, icon=icon, sort_order=sort
        )
        db.add(parent)
        db.flush()
        for child_name in children:
            db.add(CatModel(
                name=child_name, type=1, parent_id=parent.id,
                sort_order=sort
            ))
        sort += 1

    for name, icon, children in income_categories:
        parent = CatModel(
            name=name, type=2, icon=icon, sort_order=sort
        )
        db.add(parent)
        db.flush()
        for child_name in children:
            db.add(CatModel(
                name=child_name, type=2, parent_id=parent.id,
                sort_order=sort
            ))
        sort += 1

    db.commit()


def _seed_default_account(db):
    """
    创建默认资金账户。

    当账户表为空时，创建一个"现金"默认账户。

    Args:
        db: SQLAlchemy数据库会话
    """
    from app.models import Account as AccModel
    if db.query(AccModel).first() is not None:
        return

    default = AccModel(
        name="现金",
        type=1,
        icon="cash",
        color="#4CAF50",
        balance=0,
        initial_balance=0,
        is_default=1,
        sort_order=0,
    )
    db.add(default)
    db.commit()
