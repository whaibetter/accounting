import os
import logging
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

logger = logging.getLogger("database")

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
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.models import User, Account, Category, Tag, Bill, BillTag, SystemConfig, OperationLog  # noqa: F401
    Base.metadata.create_all(bind=engine)

    _migrate_db()

    from app.auth import init_auth
    init_auth()

    db = SessionLocal()
    try:
        _assign_orphan_data_to_admin(db)
        _ensure_admin_role(db)
        _seed_categories(db)
        _seed_default_account(db)
    finally:
        db.close()


def _migrate_db():
    import sqlalchemy
    insp = sqlalchemy.inspect(engine)

    if 'tag' in insp.get_table_names():
        tag_columns = [col['name'] for col in insp.get_columns('tag')]
        if 'icon' not in tag_columns:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE tag ADD COLUMN icon VARCHAR(50) DEFAULT ''"))
                conn.commit()

    if 'account' in insp.get_table_names():
        account_columns = [col['name'] for col in insp.get_columns('account')]
        if 'user_id' not in account_columns:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE account ADD COLUMN user_id INTEGER"))
                conn.commit()
            logger.info("已为account表添加user_id列")

    if 'category' in insp.get_table_names():
        category_columns = [col['name'] for col in insp.get_columns('category')]
        if 'user_id' not in category_columns:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE category ADD COLUMN user_id INTEGER"))
                conn.commit()
            logger.info("已为category表添加user_id列")

    if 'tag' in insp.get_table_names():
        tag_columns = [col['name'] for col in insp.get_columns('tag')]
        if 'user_id' not in tag_columns:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE tag ADD COLUMN user_id INTEGER"))
                conn.commit()
            logger.info("已为tag表添加user_id列")

    if 'user' in insp.get_table_names():
        user_columns = [col['name'] for col in insp.get_columns('user')]
        if 'is_admin' not in user_columns:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE \"user\" ADD COLUMN is_admin INTEGER DEFAULT 0"))
                conn.commit()
            logger.info("已为user表添加is_admin列")
        if 'status' not in user_columns:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE \"user\" ADD COLUMN status INTEGER DEFAULT 1"))
                conn.commit()
            logger.info("已为user表添加status列")

    if 'account' in insp.get_table_names():
        with engine.connect() as conn:
            try:
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_account_user_id ON account(user_id)"))
                conn.commit()
            except Exception:
                pass
    if 'category' in insp.get_table_names():
        with engine.connect() as conn:
            try:
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_category_user_id ON category(user_id)"))
                conn.commit()
            except Exception:
                pass
    if 'tag' in insp.get_table_names():
        with engine.connect() as conn:
            try:
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_tag_user_id ON tag(user_id)"))
                conn.commit()
            except Exception:
                pass

    if 'operation_log' in insp.get_table_names():
        log_columns = [col['name'] for col in insp.get_columns('operation_log')]
        new_cols = {
            'method': "VARCHAR(10) DEFAULT ''",
            'path': "VARCHAR(200) DEFAULT ''",
            'status': "VARCHAR(20) DEFAULT 'success'",
            'duration_ms': "INTEGER",
            'extra_data': "TEXT",
        }
        for col_name, col_def in new_cols.items():
            if col_name not in log_columns:
                with engine.connect() as conn:
                    conn.execute(text(f"ALTER TABLE operation_log ADD COLUMN {col_name} {col_def}"))
                    conn.commit()
                logger.info(f"已为operation_log表添加{col_name}列")
        with engine.connect() as conn:
            try:
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_operation_log_operator_id ON operation_log(operator_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_operation_log_action ON operation_log(action)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_operation_log_created_at ON operation_log(created_at)"))
                conn.commit()
            except Exception:
                pass


def _assign_orphan_data_to_admin(db):
    from app.models import User, Account, Category, Tag

    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        return

    orphan_accounts = db.query(Account).filter(Account.user_id.is_(None)).all()
    if orphan_accounts:
        for acc in orphan_accounts:
            acc.user_id = admin.id
        db.commit()
        logger.info(f"已将 {len(orphan_accounts)} 个孤立账户分配给admin用户")

    orphan_categories = db.query(Category).filter(Category.user_id.is_(None)).all()
    if orphan_categories:
        for cat in orphan_categories:
            cat.user_id = admin.id
        db.commit()
        logger.info(f"已将 {len(orphan_categories)} 个孤立分类分配给admin用户")

    orphan_tags = db.query(Tag).filter(Tag.user_id.is_(None)).all()
    if orphan_tags:
        for tag in orphan_tags:
            tag.user_id = admin.id
        db.commit()
        logger.info(f"已将 {len(orphan_tags)} 个孤立标签分配给admin用户")


def _seed_categories(db):
    from app.models import Category as CatModel, User

    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        return

    if db.query(CatModel).filter(CatModel.user_id == admin.id).first() is not None:
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
        parent = CatModel(user_id=admin.id, name=name, type=1, icon=icon, sort_order=sort)
        db.add(parent)
        db.flush()
        for child_name in children:
            db.add(CatModel(user_id=admin.id, name=child_name, type=1, parent_id=parent.id, sort_order=sort))
        sort += 1

    for name, icon, children in income_categories:
        parent = CatModel(user_id=admin.id, name=name, type=2, icon=icon, sort_order=sort)
        db.add(parent)
        db.flush()
        for child_name in children:
            db.add(CatModel(user_id=admin.id, name=child_name, type=2, parent_id=parent.id, sort_order=sort))
        sort += 1

    db.commit()


def _seed_default_account(db):
    from app.models import Account as AccModel, User

    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        return

    if db.query(AccModel).filter(AccModel.user_id == admin.id).first() is not None:
        return

    default = AccModel(
        user_id=admin.id,
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


def _ensure_admin_role(db):
    from app.models import User

    admin = db.query(User).filter(User.username == "admin").first()
    if admin and admin.is_admin != 1:
        admin.is_admin = 1
        db.commit()
        logger.info("已将admin用户设置为管理员")
