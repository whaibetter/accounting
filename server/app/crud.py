"""
数据库CRUD操作模块。

功能描述：
    封装所有数据库的增删改查操作，供路由层调用。
    每个函数对应一个具体的数据库操作，包含完整的参数校验和异常处理。

使用方法：
    from app.crud import (
        get_accounts, create_account, update_account, delete_account,
        get_bills, create_bill, update_bill, delete_bill,
        get_categories, create_category, update_category, delete_category,
        get_tags, create_tag, update_tag, delete_tag,
        get_overview, get_category_stats, get_trend,
    )

参数说明：
    db: SQLAlchemy Session 对象
    其余参数见各函数文档

异常处理：
    - 资源不存在时返回 None（由路由层判断并抛出HTTPException）
    - 唯一约束冲突时抛出 IntegrityError（由路由层捕获处理）
"""

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Account, Bill, BillTag, Category, Tag


# ==================== Account CRUD ====================

def get_accounts(db: Session) -> List[Account]:
    """
    获取所有资金账户列表。

    Args:
        db: 数据库会话

    Returns:
        List[Account]: 账户列表，按sort_order排序
    """
    return db.query(Account).order_by(Account.sort_order).all()


def get_account(db: Session, account_id: int) -> Optional[Account]:
    """
    根据ID获取单个资金账户。

    Args:
        db: 数据库会话
        account_id: 账户ID

    Returns:
        Account | None: 账户对象，不存在则返回None
    """
    return db.query(Account).filter(Account.id == account_id).first()


def create_account(db: Session, name: str, type_: int, icon: str = "",
                   color: str = "", initial_balance: float = 0,
                   is_default: bool = False) -> Account:
    """
    创建资金账户。

    如果设为默认账户，会取消其他账户的默认状态。
    账户余额初始化为initial_balance。

    Args:
        db: 数据库会话
        name: 账户名称
        type_: 账户类型 (1-6)
        icon: 图标标识
        color: 颜色标识
        initial_balance: 初始余额
        is_default: 是否默认账户

    Returns:
        Account: 新创建的账户对象
    """
    if is_default:
        db.query(Account).filter(Account.is_default == 1).update({"is_default": 0})

    account = Account(
        name=name,
        type=type_,
        icon=icon,
        color=color,
        balance=initial_balance,
        initial_balance=initial_balance,
        is_default=1 if is_default else 0,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def update_account(db: Session, account_id: int, **kwargs) -> Optional[Account]:
    """
    更新资金账户信息。

    仅更新传入的非None字段。

    Args:
        db: 数据库会话
        account_id: 账户ID
        **kwargs: 需要更新的字段键值对

    Returns:
        Account | None: 更新后的账户对象，不存在则返回None
    """
    account = get_account(db, account_id)
    if not account:
        return None

    for key, value in kwargs.items():
        if value is not None:
            setattr(account, key, value)

    db.commit()
    db.refresh(account)
    return account


def delete_account(db: Session, account_id: int) -> bool:
    """
    删除资金账户。

    如果账户下存在账单记录，则不允许删除。

    Args:
        db: 数据库会话
        account_id: 账户ID

    Returns:
        bool: 是否删除成功

    Raises:
        ValueError: 账户下存在账单记录时
    """
    account = get_account(db, account_id)
    if not account:
        return False

    bill_count = db.query(Bill).filter(
        (Bill.account_id == account_id) | (Bill.transfer_to_account_id == account_id)
    ).count()
    if bill_count > 0:
        raise ValueError("该账户下存在账单记录，无法删除")

    db.delete(account)
    db.commit()
    return True


# ==================== Category CRUD ====================

def get_categories(db: Session, type_: Optional[int] = None) -> List[Category]:
    """
    获取分类列表（仅顶级分类）。

    Args:
        db: 数据库会话
        type_: 分类类型筛选 (1-支出, 2-收入, None-全部)

    Returns:
        List[Category]: 顶级分类列表，每个包含children子分类
    """
    query = db.query(Category).filter(Category.parent_id.is_(None))
    if type_ is not None:
        query = query.filter(Category.type == type_)
    return query.order_by(Category.sort_order).all()


def get_category(db: Session, category_id: int) -> Optional[Category]:
    """
    根据ID获取单个分类。

    Args:
        db: 数据库会话
        category_id: 分类ID

    Returns:
        Category | None: 分类对象
    """
    return db.query(Category).filter(Category.id == category_id).first()


def create_category(db: Session, name: str, type_: int, parent_id: Optional[int] = None,
                    icon: str = "") -> Category:
    """
    创建分类。

    如果指定parent_id，则创建子分类，且类型继承父分类。

    Args:
        db: 数据库会话
        name: 分类名称
        type_: 分类类型 (1-支出, 2-收入)
        parent_id: 父分类ID (None为顶级分类)
        icon: 图标标识

    Returns:
        Category: 新创建的分类对象

    Raises:
        ValueError: 父分类不存在时
    """
    if parent_id is not None:
        parent = get_category(db, parent_id)
        if not parent:
            raise ValueError("父分类不存在")
        type_ = parent.type

    max_sort = db.query(func.max(Category.sort_order)).scalar() or 0
    category = Category(
        name=name, type=type_, parent_id=parent_id,
        icon=icon, sort_order=max_sort + 1
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category_id: int, **kwargs) -> Optional[Category]:
    """
    更新分类信息。

    Args:
        db: 数据库会话
        category_id: 分类ID
        **kwargs: 需要更新的字段

    Returns:
        Category | None: 更新后的分类对象
    """
    category = get_category(db, category_id)
    if not category:
        return None

    for key, value in kwargs.items():
        if value is not None:
            setattr(category, key, value)

    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> bool:
    """
    删除分类。

    如果分类下存在子分类或账单记录，则不允许删除。

    Args:
        db: 数据库会话
        category_id: 分类ID

    Returns:
        bool: 是否删除成功

    Raises:
        ValueError: 存在子分类或关联账单时
    """
    category = get_category(db, category_id)
    if not category:
        return False

    child_count = db.query(Category).filter(Category.parent_id == category_id).count()
    if child_count > 0:
        raise ValueError("该分类下存在子分类，无法删除")

    bill_count = db.query(Bill).filter(Bill.category_id == category_id).count()
    if bill_count > 0:
        raise ValueError("该分类下存在账单记录，无法删除")

    db.delete(category)
    db.commit()
    return True


# ==================== Tag CRUD ====================

def get_tags(db: Session) -> List[Tag]:
    """
    获取所有标签列表。

    Args:
        db: 数据库会话

    Returns:
        List[Tag]: 标签列表
    """
    return db.query(Tag).order_by(Tag.id).all()


def get_tag(db: Session, tag_id: int) -> Optional[Tag]:
    """
    根据ID获取单个标签。

    Args:
        db: 数据库会话
        tag_id: 标签ID

    Returns:
        Tag | None: 标签对象
    """
    return db.query(Tag).filter(Tag.id == tag_id).first()


def create_tag(db: Session, name: str, color: str = "") -> Tag:
    """
    创建标签。

    Args:
        db: 数据库会话
        name: 标签名称 (唯一)
        color: 颜色标识

    Returns:
        Tag: 新创建的标签对象

    Raises:
        ValueError: 标签名称已存在时
    """
    existing = db.query(Tag).filter(Tag.name == name).first()
    if existing:
        raise ValueError(f"标签 '{name}' 已存在")

    tag = Tag(name=name, color=color)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def update_tag(db: Session, tag_id: int, **kwargs) -> Optional[Tag]:
    """
    更新标签信息。

    Args:
        db: 数据库会话
        tag_id: 标签ID
        **kwargs: 需要更新的字段

    Returns:
        Tag | None: 更新后的标签对象
    """
    tag = get_tag(db, tag_id)
    if not tag:
        return None

    for key, value in kwargs.items():
        if value is not None:
            setattr(tag, key, value)

    db.commit()
    db.refresh(tag)
    return tag


def delete_tag(db: Session, tag_id: int) -> bool:
    """
    删除标签。

    同时删除该标签与所有账单的关联关系。

    Args:
        db: 数据库会话
        tag_id: 标签ID

    Returns:
        bool: 是否删除成功
    """
    tag = get_tag(db, tag_id)
    if not tag:
        return False

    db.query(BillTag).filter(BillTag.tag_id == tag_id).delete()
    db.delete(tag)
    db.commit()
    return True


# ==================== Bill CRUD ====================

def get_bills(db: Session, page: int = 1, size: int = 20,
              start_date: Optional[date] = None, end_date: Optional[date] = None,
              type_: Optional[int] = None, category_id: Optional[int] = None,
              account_id: Optional[int] = None, keyword: Optional[str] = None) -> dict:
    """
    获取账单列表（分页+筛选）。

    Args:
        db: 数据库会话
        page: 页码 (从1开始)
        size: 每页大小
        start_date: 开始日期筛选
        end_date: 结束日期筛选
        type_: 类型筛选 (1-支出, 2-收入, 3-转账)
        category_id: 分类ID筛选
        account_id: 账户ID筛选
        keyword: 关键词搜索 (匹配备注)

    Returns:
        dict: {"items": [...], "total": int, "page": int, "size": int}
    """
    query = db.query(Bill)

    if start_date:
        query = query.filter(Bill.bill_date >= start_date)
    if end_date:
        query = query.filter(Bill.bill_date <= end_date)
    if type_ is not None:
        query = query.filter(Bill.type == type_)
    if category_id is not None:
        query = query.filter(Bill.category_id == category_id)
    if account_id is not None:
        query = query.filter(Bill.account_id == account_id)
    if keyword:
        query = query.filter(Bill.remark.contains(keyword))

    total = query.count()
    items = (query.order_by(Bill.bill_date.desc(), Bill.bill_time.desc())
             .offset((page - 1) * size).limit(size).all())

    return {"items": items, "total": total, "page": page, "size": size}


def get_bill(db: Session, bill_id: int) -> Optional[Bill]:
    """
    根据ID获取单个账单。

    Args:
        db: 数据库会话
        bill_id: 账单ID

    Returns:
        Bill | None: 账单对象
    """
    return db.query(Bill).filter(Bill.id == bill_id).first()


def create_bill(db: Session, account_id: int, category_id: int, type_: int,
                amount: float, bill_date: date, bill_time=None, remark: str = "",
                tag_ids: Optional[List[int]] = None,
                transfer_to_account_id: Optional[int] = None) -> Bill:
    """
    创建账单。

    创建账单时会自动更新关联账户的余额：
    - 支出：从账户扣减金额
    - 收入：向账户增加金额
    - 转账：从源账户扣减，向目标账户增加

    Args:
        db: 数据库会话
        account_id: 资金账户ID
        category_id: 分类ID
        type_: 类型 (1-支出, 2-收入, 3-转账)
        amount: 金额
        bill_date: 账单日期
        bill_time: 账单时间
        remark: 备注
        tag_ids: 关联标签ID列表
        transfer_to_account_id: 转入账户ID

    Returns:
        Bill: 新创建的账单对象

    Raises:
        ValueError: 账户不存在、分类不存在、标签不存在时
    """
    account = get_account(db, account_id)
    if not account:
        raise ValueError("资金账户不存在")

    category = get_category(db, category_id)
    if not category:
        raise ValueError("分类不存在")

    transfer_account = None
    if type_ == 3:
        if not transfer_to_account_id:
            raise ValueError("转账类型必须指定转入账户")
        transfer_account = get_account(db, transfer_to_account_id)
        if not transfer_account:
            raise ValueError("转入账户不存在")

    bill = Bill(
        account_id=account_id,
        category_id=category_id,
        type=type_,
        amount=amount,
        bill_date=bill_date,
        bill_time=bill_time,
        remark=remark,
        transfer_to_account_id=transfer_to_account_id,
    )
    db.add(bill)
    db.flush()

    if tag_ids:
        for tag_id in tag_ids:
            tag = get_tag(db, tag_id)
            if not tag:
                raise ValueError(f"标签ID {tag_id} 不存在")
            db.add(BillTag(bill_id=bill.id, tag_id=tag_id))

    if type_ == 1:
        account.balance -= amount
    elif type_ == 2:
        account.balance += amount
    elif type_ == 3:
        account.balance -= amount
        transfer_account.balance += amount

    db.commit()
    db.refresh(bill)
    return bill


def update_bill(db: Session, bill_id: int, **kwargs) -> Optional[Bill]:
    """
    更新账单信息。

    更新账单时会重新计算账户余额变动。

    Args:
        db: 数据库会话
        bill_id: 账单ID
        **kwargs: 需要更新的字段

    Returns:
        Bill | None: 更新后的账单对象
    """
    bill = get_bill(db, bill_id)
    if not bill:
        return None

    old_type = bill.type
    old_amount = bill.amount
    old_account_id = bill.account_id
    old_transfer_to = bill.transfer_to_account_id

    tag_ids = kwargs.pop("tag_ids", None)

    for key, value in kwargs.items():
        if value is not None:
            setattr(bill, key, value)

    if tag_ids is not None:
        db.query(BillTag).filter(BillTag.bill_id == bill_id).delete()
        for tag_id in tag_ids:
            db.add(BillTag(bill_id=bill_id, tag_id=tag_id))

    _revert_balance(db, old_type, old_amount, old_account_id, old_transfer_to)

    new_type = bill.type
    new_amount = bill.amount
    new_account = get_account(db, bill.account_id)
    new_transfer = get_account(db, bill.transfer_to_account_id) if bill.transfer_to_account_id else None

    if new_type == 1:
        new_account.balance -= new_amount
    elif new_type == 2:
        new_account.balance += new_amount
    elif new_type == 3 and new_transfer:
        new_account.balance -= new_amount
        new_transfer.balance += new_amount

    db.commit()
    db.refresh(bill)
    return bill


def _revert_balance(db: Session, bill_type: int, amount: float,
                    account_id: int, transfer_to_account_id: Optional[int]):
    """
    撤销账单对账户余额的影响。

    在更新或删除账单时使用，先撤销旧账单的余额变动，
    再应用新账单的余额变动。

    Args:
        db: 数据库会话
        bill_type: 账单类型
        amount: 金额
        account_id: 账户ID
        transfer_to_account_id: 转入账户ID
    """
    account = get_account(db, account_id)
    if not account:
        return

    if bill_type == 1:
        account.balance += amount
    elif bill_type == 2:
        account.balance -= amount
    elif bill_type == 3:
        account.balance += amount
        if transfer_to_account_id:
            transfer_account = get_account(db, transfer_to_account_id)
            if transfer_account:
                transfer_account.balance -= amount


def delete_bill(db: Session, bill_id: int) -> bool:
    """
    删除账单。

    删除时自动撤销对账户余额的影响。

    Args:
        db: 数据库会话
        bill_id: 账单ID

    Returns:
        bool: 是否删除成功
    """
    bill = get_bill(db, bill_id)
    if not bill:
        return False

    _revert_balance(db, bill.type, bill.amount, bill.account_id, bill.transfer_to_account_id)

    db.query(BillTag).filter(BillTag.bill_id == bill_id).delete()
    db.delete(bill)
    db.commit()
    return True


# ==================== Statistics ====================

def get_overview(db: Session, start_date: Optional[date] = None,
                 end_date: Optional[date] = None) -> dict:
    """
    获取收支概览。

    Args:
        db: 数据库会话
        start_date: 开始日期
        end_date: 结束日期

    Returns:
        dict: {"total_income": float, "total_expense": float, "balance": float, "bill_count": int}
    """
    query = db.query(Bill)
    if start_date:
        query = query.filter(Bill.bill_date >= start_date)
    if end_date:
        query = query.filter(Bill.bill_date <= end_date)

    income = query.filter(Bill.type == 2).with_entities(func.sum(Bill.amount)).scalar() or 0
    expense = query.filter(Bill.type == 1).with_entities(func.sum(Bill.amount)).scalar() or 0
    transfer_out = query.filter(Bill.type == 3).with_entities(func.sum(Bill.amount)).scalar() or 0
    bill_count = query.count()

    return {
        "total_income": float(income),
        "total_expense": float(expense + transfer_out),
        "balance": float(income - expense - transfer_out),
        "bill_count": bill_count,
    }


def get_category_stats(db: Session, start_date: Optional[date] = None,
                       end_date: Optional[date] = None,
                       type_: int = 1) -> List[dict]:
    """
    获取分类统计数据。

    仅统计顶级分类，子分类金额汇总到父分类。

    Args:
        db: 数据库会话
        start_date: 开始日期
        end_date: 结束日期
        type_: 类型 (1-支出, 2-收入)

    Returns:
        List[dict]: 分类统计列表，每项包含category_id, category_name, category_icon, amount, percentage, bill_count
    """
    parent_categories = db.query(Category).filter(
        Category.parent_id.is_(None), Category.type == type_
    ).all()

    total_amount = 0
    stats = []

    for cat in parent_categories:
        child_ids = [c.id for c in cat.children] + [cat.id]
        query = db.query(Bill).filter(
            Bill.category_id.in_(child_ids), Bill.type == type_
        )
        if start_date:
            query = query.filter(Bill.bill_date >= start_date)
        if end_date:
            query = query.filter(Bill.bill_date <= end_date)

        amount = query.with_entities(func.sum(Bill.amount)).scalar() or 0
        count = query.count()

        if amount > 0:
            stats.append({
                "category_id": cat.id,
                "category_name": cat.name,
                "category_icon": cat.icon,
                "amount": float(amount),
                "bill_count": count,
            })
            total_amount += float(amount)

    for stat in stats:
        stat["percentage"] = round(stat["amount"] / total_amount * 100, 1) if total_amount > 0 else 0

    stats.sort(key=lambda x: x["amount"], reverse=True)
    return stats


def get_trend(db: Session, start_date: date, end_date: date,
              granularity: str = "month") -> List[dict]:
    """
    获取收支趋势数据。

    Args:
        db: 数据库会话
        start_date: 开始日期
        end_date: 结束日期
        granularity: 粒度 ("month" 或 "day")

    Returns:
        List[dict]: 趋势数据列表，每项包含period, income, expense
    """
    bills = db.query(Bill).filter(
        Bill.bill_date >= start_date, Bill.bill_date <= end_date
    ).all()

    grouped = {}
    for bill in bills:
        if granularity == "month":
            key = bill.bill_date.strftime("%Y-%m")
        else:
            key = bill.bill_date.strftime("%Y-%m-%d")

        if key not in grouped:
            grouped[key] = {"income": 0, "expense": 0}

        if bill.type == 2:
            grouped[key]["income"] += bill.amount
        elif bill.type in (1, 3):
            grouped[key]["expense"] += bill.amount

    result = []
    for period in sorted(grouped.keys()):
        result.append({
            "period": period,
            "income": round(grouped[period]["income"], 2),
            "expense": round(grouped[period]["expense"], 2),
        })

    return result


def get_balance_trend(db: Session, start_date: date, end_date: date,
                      account_id: Optional[int] = None) -> List[dict]:
    """
    获取账户余额趋势数据。

    计算每个账户在指定日期范围内每天的余额变化。
    通过从当前余额倒推计算历史余额。

    Args:
        db: 数据库会话
        start_date: 开始日期
        end_date: 结束日期
        account_id: 账户ID (None表示所有账户)

    Returns:
        List[dict]: 账户余额趋势列表，每项包含account_id, account_name, data
    """
    accounts = db.query(Account).all()
    if account_id:
        accounts = [a for a in accounts if a.id == account_id]

    result = []
    for account in accounts:
        current_balance = account.balance

        bills = db.query(Bill).filter(
            Bill.bill_date >= start_date,
            Bill.bill_date <= end_date,
            ((Bill.account_id == account.id) | (Bill.transfer_to_account_id == account.id))
        ).order_by(Bill.bill_date.desc()).all()

        date_balance = {}
        current_date = end_date
        temp_balance = current_balance

        while current_date >= start_date:
            date_str = current_date.strftime("%Y-%m-%d")
            date_balance[date_str] = temp_balance
            current_date = date.fromordinal(current_date.toordinal() - 1)

        for bill in bills:
            bill_date_str = bill.bill_date.strftime("%Y-%m-%d")
            if bill_date_str in date_balance:
                if bill.account_id == account.id:
                    if bill.type == 1:
                        temp_balance += bill.amount
                    elif bill.type == 2:
                        temp_balance -= bill.amount
                    elif bill.type == 3:
                        temp_balance += bill.amount
                elif bill.transfer_to_account_id == account.id:
                    temp_balance -= bill.amount

                for d in sorted(date_balance.keys()):
                    if d <= bill_date_str:
                        date_balance[d] = temp_balance

        data = []
        for d in sorted(date_balance.keys()):
            data.append({
                "date": d,
                "balance": round(date_balance[d], 2)
            })

        result.append({
            "account_id": account.id,
            "account_name": account.name,
            "data": data
        })

    return result


# ==================== Batch Import ====================

def import_accounts_batch(db: Session, accounts: List[dict]) -> dict:
    """
    批量导入账户。

    根据账户名称去重，已存在则跳过。

    Args:
        db: 数据库会话
        accounts: 账户列表，每项包含name, type, icon, color, initial_balance

    Returns:
        dict: {"success": int, "skipped": int, "errors": List[str]}
    """
    success = 0
    skipped = 0
    errors = []

    for item in accounts:
        try:
            name = item.get("name")
            if not name:
                errors.append(f"缺少账户名称: {item}")
                continue

            existing = db.query(Account).filter(Account.name == name).first()
            if existing:
                skipped += 1
                continue

            acc = Account(
                name=name,
                type=item.get("type", 1),
                icon=item.get("icon", ""),
                color=item.get("color", ""),
                balance=item.get("initial_balance", 0) or 0,
                initial_balance=item.get("initial_balance", 0) or 0,
            )
            db.add(acc)
            success += 1
        except Exception as e:
            errors.append(f"导入账户 '{item.get('name')}' 失败: {str(e)}")

    db.commit()
    return {"success": success, "skipped": skipped, "errors": errors}


def import_bills_batch(db: Session, bills: List[dict], account_name_map: dict) -> dict:
    """
    批量导入账单。

    支持按账户名称和分类名称自动匹配。

    Args:
        db: 数据库会话
        bills: 账单列表
        account_name_map: 账户名称->ID的映射字典

    Returns:
        dict: {"success": int, "errors": List[dict]}
            errors每项包含 index, original, reason
    """
    success = 0
    errors = []

    category_cache = {}

    def get_category_id(cat_name: str, bill_type: int) -> Optional[int]:
        """根据分类名称查找分类ID（支持模糊匹配）。"""
        cache_key = f"{cat_name}_{bill_type}"
        if cache_key in category_cache:
            return category_cache[cache_key]

        cats = db.query(Category).filter(
            Category.name == cat_name, Category.type == bill_type
        ).all()

        if len(cats) == 1:
            category_cache[cache_key] = cats[0].id
            return cats[0].id

        for cat in cats:
            if cat.parent_id is None:
                category_cache[cache_key] = cat.id
                return cat.id

        for cat in cats:
            if cat_name in cat.name or cat.name in cat_name:
                category_cache[cache_key] = cat.id
                return cat.id

        all_cats = db.query(Category).filter(Category.type == bill_type).all()
        for cat in all_cats:
            if cat_name == cat.name or cat_name in cat.name:
                category_cache[cache_key] = cat.id
                return cat.id

        category_cache[cache_key] = None
        return None

    for i, item in enumerate(bills):
        try:
            account_name = item.get("account")
            category_name = item.get("category")
            bill_type = item.get("type", 1)

            if bill_type == 3:
                bill_type = 1

            if not account_name:
                errors.append({
                    "index": i, "original": item,
                    "reason": f"缺少账户名称"
                })
                continue

            account_id = account_name_map.get(account_name)
            if not account_id:
                errors.append({
                    "index": i, "original": item,
                    "reason": f"未找到账户 '{account_name}'"
                })
                continue

            category_id = None
            if category_name:
                category_id = get_category_id(category_name, bill_type)
            if not category_id:
                errors.append({
                    "index": i, "original": item,
                    "reason": f"未找到分类 '{category_name}'"
                })
                continue

            amount = float(item.get("amount", 0))
            if amount <= 0:
                errors.append({
                    "index": i, "original": item,
                    "reason": f"金额必须大于0"
                })
                continue

            bill_date_str = item.get("date") or item.get("bill_date")
            if not bill_date_str:
                errors.append({
                    "index": i, "original": item,
                    "reason": "缺少日期"
                })
                continue

            from datetime import datetime as dt
            try:
                bill_date = dt.strptime(str(bill_date_str), "%Y-%m-%d").date()
            except ValueError:
                try:
                    bill_date = dt.strptime(str(bill_date_str), "%Y/%m/%d").date()
                except ValueError:
                    errors.append({
                        "index": i, "original": item,
                        "reason": f"日期格式错误 '{bill_date_str}'，应为 YYYY-MM-DD"
                    })
                    continue

            bill_time_str = item.get("time") or item.get("bill_time")
            bill_time = None
            if bill_time_str:
                try:
                    bill_time = dt.strptime(str(bill_time_str), "%H:%M").time()
                except ValueError:
                    try:
                        bill_time = dt.strptime(str(bill_time_str), "%H:%M:%S").time()
                    except ValueError:
                        pass

            tag_ids = item.get("tag_ids") or []
            if isinstance(tag_ids, list) and len(tag_ids) > 0 and isinstance(tag_ids[0], str):
                tag_ids = []

            b = Bill(
                account_id=account_id,
                category_id=category_id,
                type=bill_type,
                amount=amount,
                bill_date=bill_date,
                bill_time=bill_time,
                remark=str(item.get("remark") or ""),
            )
            db.add(b)
            db.flush()

            for tag_id in tag_ids:
                db.add(BillTag(bill_id=b.id, tag_id=tag_id))

            if bill_type == 1:
                acc = db.query(Account).filter(Account.id == account_id).first()
                if acc:
                    acc.balance -= amount
            elif bill_type == 2:
                acc = db.query(Account).filter(Account.id == account_id).first()
                if acc:
                    acc.balance += amount

            success += 1
        except Exception as e:
            errors.append({
                "index": i, "original": item,
                "reason": f"处理失败: {str(e)}"
            })

    db.commit()
    return {"success": success, "errors": errors}
