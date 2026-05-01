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
        2. 初始化认证系统（密码哈希、JWT密钥、默认用户和分类）

    此函数应在应用启动时调用一次。
    """
    from app.models import Account, Category, SystemConfig  # noqa: F401
    Base.metadata.create_all(bind=engine)

    from app.auth import init_auth
    init_auth()


