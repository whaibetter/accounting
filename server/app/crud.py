from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Account, Bill, BillTag, Category, Tag


# ==================== Account CRUD ====================

def get_accounts(db: Session, user_id: int) -> List[Account]:
    return db.query(Account).filter(Account.user_id == user_id).order_by(Account.sort_order).all()


def get_account(db: Session, account_id: int, user_id: int) -> Optional[Account]:
    return db.query(Account).filter(Account.id == account_id, Account.user_id == user_id).first()


def create_account(db: Session, user_id: int, name: str, type_: int, icon: str = "",
                   color: str = "", initial_balance: float = 0,
                   is_default: bool = False) -> Account:
    if is_default:
        db.query(Account).filter(Account.user_id == user_id, Account.is_default == 1).update({"is_default": 0})

    account = Account(
        user_id=user_id,
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


def update_account(db: Session, account_id: int, user_id: int, **kwargs) -> Optional[Account]:
    account = get_account(db, account_id, user_id)
    if not account:
        return None

    for key, value in kwargs.items():
        if value is not None:
            setattr(account, key, value)

    db.commit()
    db.refresh(account)
    return account


def delete_account(db: Session, account_id: int, user_id: int) -> bool:
    account = get_account(db, account_id, user_id)
    if not account:
        return False

    bill_count = db.query(Bill).filter(
        Bill.account_id == account_id
    ).join(Account, Bill.account_id == Account.id).filter(Account.user_id == user_id).count()
    if bill_count > 0:
        raise ValueError("该账户下存在账单记录，无法删除")

    db.delete(account)
    db.commit()
    return True


# ==================== Category CRUD ====================

def get_categories(db: Session, user_id: int, type_: Optional[int] = None) -> List[Category]:
    query = db.query(Category).filter(Category.user_id == user_id, Category.parent_id.is_(None))
    if type_ is not None:
        query = query.filter(Category.type == type_)
    return query.order_by(Category.sort_order).all()


def get_category(db: Session, category_id: int, user_id: int) -> Optional[Category]:
    return db.query(Category).filter(Category.id == category_id, Category.user_id == user_id).first()


def create_category(db: Session, user_id: int, name: str, type_: int, parent_id: Optional[int] = None,
                    icon: str = "") -> Category:
    if parent_id is not None:
        parent = get_category(db, parent_id, user_id)
        if not parent:
            raise ValueError("父分类不存在")
        type_ = parent.type

    max_sort = db.query(func.max(Category.sort_order)).filter(Category.user_id == user_id).scalar() or 0
    category = Category(
        user_id=user_id, name=name, type=type_, parent_id=parent_id,
        icon=icon, sort_order=max_sort + 1
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category_id: int, user_id: int, **kwargs) -> Optional[Category]:
    category = get_category(db, category_id, user_id)
    if not category:
        return None

    if "parent_id" in kwargs:
        new_parent_id = kwargs["parent_id"]
        if new_parent_id is not None:
            if new_parent_id == category_id:
                raise ValueError("不能将分类设为自身的子分类")
            child_ids = [c.id for c in db.query(Category).filter(
                Category.parent_id == category_id, Category.user_id == user_id
            ).all()]
            if new_parent_id in child_ids:
                raise ValueError("不能将分类转移到其子分类下")
            parent = get_category(db, new_parent_id, user_id)
            if not parent:
                raise ValueError("父分类不存在")
            category.type = parent.type

    for key, value in kwargs.items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int, user_id: int, cascade: bool = False) -> bool:
    category = get_category(db, category_id, user_id)
    if not category:
        return False

    child_count = db.query(Category).filter(
        Category.parent_id == category_id, Category.user_id == user_id
    ).count()
    if child_count > 0 and not cascade:
        raise ValueError("该分类下存在子分类，无法删除。请先删除或转移子分类，或使用级联删除。")

    bill_count = db.query(Bill).filter(Bill.category_id == category_id).count()
    if bill_count > 0:
        raise ValueError("该分类下存在账单记录，无法删除")

    if cascade and child_count > 0:
        children = db.query(Category).filter(
            Category.parent_id == category_id, Category.user_id == user_id
        ).all()
        for child in children:
            child_bill_count = db.query(Bill).filter(Bill.category_id == child.id).count()
            if child_bill_count > 0:
                raise ValueError(f"子分类「{child.name}」下存在账单记录，无法级联删除")
            db.delete(child)

    db.delete(category)
    db.commit()
    return True


# ==================== Tag CRUD ====================

def get_tags(db: Session, user_id: int) -> List[Tag]:
    return db.query(Tag).filter(Tag.user_id == user_id).order_by(Tag.id).all()


def get_tag(db: Session, tag_id: int, user_id: int) -> Optional[Tag]:
    return db.query(Tag).filter(Tag.id == tag_id, Tag.user_id == user_id).first()


def create_tag(db: Session, user_id: int, name: str, color: str = "", icon: str = "") -> Tag:
    existing = db.query(Tag).filter(Tag.name == name, Tag.user_id == user_id).first()
    if existing:
        raise ValueError(f"标签 '{name}' 已存在")

    tag = Tag(user_id=user_id, name=name, color=color, icon=icon)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def update_tag(db: Session, tag_id: int, user_id: int, **kwargs) -> Optional[Tag]:
    tag = get_tag(db, tag_id, user_id)
    if not tag:
        return None

    for key, value in kwargs.items():
        if value is not None:
            setattr(tag, key, value)

    db.commit()
    db.refresh(tag)
    return tag


def delete_tag(db: Session, tag_id: int, user_id: int) -> bool:
    tag = get_tag(db, tag_id, user_id)
    if not tag:
        return False

    db.query(BillTag).filter(BillTag.tag_id == tag_id).delete()
    db.delete(tag)
    db.commit()
    return True


# ==================== Bill CRUD ====================

def get_bills(db: Session, user_id: int, page: int = 1, size: int = 20,
              start_date: Optional[date] = None, end_date: Optional[date] = None,
              type_: Optional[int] = None, category_id: Optional[int] = None,
              account_id: Optional[int] = None, keyword: Optional[str] = None) -> dict:
    query = db.query(Bill).join(Account, Bill.account_id == Account.id).filter(Account.user_id == user_id)

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


def get_bill(db: Session, bill_id: int, user_id: int) -> Optional[Bill]:
    return db.query(Bill).join(Account, Bill.account_id == Account.id).filter(
        Bill.id == bill_id, Account.user_id == user_id
    ).first()


def create_bill(db: Session, user_id: int, account_id: int, category_id: int, type_: int,
                amount: float, bill_date: date, bill_time=None, remark: str = "",
                tag_ids: Optional[List[int]] = None,
                transfer_to_account_id: Optional[int] = None) -> Bill:
    account = get_account(db, account_id, user_id)
    if not account:
        raise ValueError("资金账户不存在")

    category = get_category(db, category_id, user_id)
    if not category:
        raise ValueError("分类不存在")

    transfer_account = None
    if type_ == 3:
        if not transfer_to_account_id:
            raise ValueError("转账类型必须指定转入账户")
        transfer_account = get_account(db, transfer_to_account_id, user_id)
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
            tag = get_tag(db, tag_id, user_id)
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


def update_bill(db: Session, bill_id: int, user_id: int, **kwargs) -> Optional[Bill]:
    bill = get_bill(db, bill_id, user_id)
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
    new_account = get_account(db, bill.account_id, user_id)
    new_transfer = get_account(db, bill.transfer_to_account_id, user_id) if bill.transfer_to_account_id else None

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
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        return

    if bill_type == 1:
        account.balance += amount
    elif bill_type == 2:
        account.balance -= amount
    elif bill_type == 3:
        account.balance += amount
        if transfer_to_account_id:
            transfer_account = db.query(Account).filter(Account.id == transfer_to_account_id).first()
            if transfer_account:
                transfer_account.balance -= amount


def delete_bill(db: Session, bill_id: int, user_id: int) -> bool:
    bill = get_bill(db, bill_id, user_id)
    if not bill:
        return False

    _revert_balance(db, bill.type, bill.amount, bill.account_id, bill.transfer_to_account_id)

    db.query(BillTag).filter(BillTag.bill_id == bill_id).delete()
    db.delete(bill)
    db.commit()
    return True


# ==================== Statistics ====================

def get_overview(db: Session, user_id: int, start_date: Optional[date] = None,
                 end_date: Optional[date] = None) -> dict:
    query = db.query(Bill).join(Account, Bill.account_id == Account.id).filter(Account.user_id == user_id)
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


def get_category_stats(db: Session, user_id: int, start_date: Optional[date] = None,
                       end_date: Optional[date] = None,
                       type_: int = 1) -> List[dict]:
    parent_categories = db.query(Category).filter(
        Category.parent_id.is_(None), Category.type == type_, Category.user_id == user_id
    ).all()

    total_amount = 0
    stats = []

    for cat in parent_categories:
        child_ids = [c.id for c in cat.children] + [cat.id]
        query = db.query(Bill).join(Account, Bill.account_id == Account.id).filter(
            Bill.category_id.in_(child_ids), Bill.type == type_, Account.user_id == user_id
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


def get_trend(db: Session, user_id: int, start_date: date, end_date: date,
              granularity: str = "month") -> List[dict]:
    bills = db.query(Bill).join(Account, Bill.account_id == Account.id).filter(
        Bill.bill_date >= start_date, Bill.bill_date <= end_date, Account.user_id == user_id
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


ACCOUNT_TYPE_NAMES = {
    1: "现金", 2: "银行卡", 3: "信用卡", 4: "支付宝", 5: "微信", 6: "其他"
}

ACCOUNT_COLORS = [
    "#6366f1", "#34d399", "#f87171", "#facc15", "#fb923c", "#a78bfa",
    "#f472b6", "#38bdf8", "#4ade80", "#e879f9", "#fbbf24", "#2dd4bf",
]


def get_balance_trend(db: Session, user_id: int, start_date: date, end_date: date,
                      account_id: Optional[int] = None,
                      account_type: Optional[int] = None) -> List[dict]:
    query = db.query(Account).filter(Account.user_id == user_id)
    if account_id:
        query = query.filter(Account.id == account_id)
    if account_type:
        query = query.filter(Account.type == account_type)
    accounts = query.order_by(Account.id).all()

    result = []
    for idx, account in enumerate(accounts):
        current_balance = account.balance

        bills = db.query(Bill).filter(
            Bill.bill_date >= start_date,
            Bill.bill_date <= end_date,
            ((Bill.account_id == account.id) | (Bill.transfer_to_account_id == account.id))
        ).order_by(Bill.bill_date.asc()).all()

        bills_by_date = {}
        for bill in bills:
            d = bill.bill_date.strftime("%Y-%m-%d")
            if d not in bills_by_date:
                bills_by_date[d] = {"income": 0, "expense": 0}
            if bill.account_id == account.id:
                if bill.type == 1:
                    bills_by_date[d]["expense"] += bill.amount
                elif bill.type == 2:
                    bills_by_date[d]["income"] += bill.amount
                elif bill.type == 3:
                    bills_by_date[d]["expense"] += bill.amount
            elif bill.transfer_to_account_id == account.id:
                bills_by_date[d]["income"] += bill.amount

        all_bills_before = db.query(Bill).filter(
            Bill.bill_date < start_date,
            ((Bill.account_id == account.id) | (Bill.transfer_to_account_id == account.id))
        ).all()

        delta_before = 0
        for bill in all_bills_before:
            if bill.account_id == account.id:
                if bill.type == 1:
                    delta_before -= bill.amount
                elif bill.type == 2:
                    delta_before += bill.amount
                elif bill.type == 3:
                    delta_before -= bill.amount
            elif bill.transfer_to_account_id == account.id:
                delta_before += bill.amount

        balance_at_start = current_balance - delta_before

        all_bills_in_range = db.query(Bill).filter(
            Bill.bill_date >= start_date,
            Bill.bill_date <= end_date,
            ((Bill.account_id == account.id) | (Bill.transfer_to_account_id == account.id))
        ).all()

        delta_in_range = 0
        for bill in all_bills_in_range:
            if bill.account_id == account.id:
                if bill.type == 1:
                    delta_in_range -= bill.amount
                elif bill.type == 2:
                    delta_in_range += bill.amount
                elif bill.type == 3:
                    delta_in_range -= bill.amount
            elif bill.transfer_to_account_id == account.id:
                delta_in_range += bill.amount

        running_balance = balance_at_start
        data = []
        current_date = start_date

        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            day_data = bills_by_date.get(date_str, {"income": 0, "expense": 0})
            running_balance += day_data["income"] - day_data["expense"]

            data.append({
                "date": date_str,
                "balance": round(running_balance, 2),
                "income": round(day_data["income"], 2),
                "expense": round(day_data["expense"], 2),
            })
            current_date = date.fromordinal(current_date.toordinal() + 1)

        result.append({
            "account_id": account.id,
            "account_name": account.name,
            "account_type": account.type,
            "account_type_name": ACCOUNT_TYPE_NAMES.get(account.type, "其他"),
            "current_balance": round(current_balance, 2),
            "color": ACCOUNT_COLORS[idx % len(ACCOUNT_COLORS)],
            "data": data
        })

    return result


# ==================== Batch Import ====================

def import_accounts_batch(db: Session, user_id: int, accounts: List[dict]) -> dict:
    success = 0
    skipped = 0
    errors = []

    for item in accounts:
        try:
            name = item.get("name")
            if not name:
                errors.append(f"缺少账户名称: {item}")
                continue

            existing = db.query(Account).filter(Account.name == name, Account.user_id == user_id).first()
            if existing:
                skipped += 1
                continue

            acc = Account(
                user_id=user_id,
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


def import_bills_batch(db: Session, user_id: int, bills: List[dict], account_name_map: dict) -> dict:
    success = 0
    errors = []

    category_cache = {}

    def get_category_id(cat_name: str, bill_type: int) -> Optional[int]:
        cache_key = f"{cat_name}_{bill_type}"
        if cache_key in category_cache:
            return category_cache[cache_key]

        cats = db.query(Category).filter(
            Category.name == cat_name, Category.type == bill_type, Category.user_id == user_id
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

        all_cats = db.query(Category).filter(Category.type == bill_type, Category.user_id == user_id).all()
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
                errors.append({"index": i, "original": item, "reason": "缺少账户名称"})
                continue

            account_id = account_name_map.get(account_name)
            if not account_id:
                errors.append({"index": i, "original": item, "reason": f"未找到账户 '{account_name}'"})
                continue

            category_id = None
            if category_name:
                category_id = get_category_id(category_name, bill_type)
            if not category_id:
                errors.append({"index": i, "original": item, "reason": f"未找到分类 '{category_name}'"})
                continue

            amount = float(item.get("amount", 0))
            if amount <= 0:
                errors.append({"index": i, "original": item, "reason": "金额必须大于0"})
                continue

            bill_date_str = item.get("date") or item.get("bill_date")
            if not bill_date_str:
                errors.append({"index": i, "original": item, "reason": "缺少日期"})
                continue

            from datetime import datetime as dt
            try:
                bill_date = dt.strptime(str(bill_date_str), "%Y-%m-%d").date()
            except ValueError:
                try:
                    bill_date = dt.strptime(str(bill_date_str), "%Y/%m/%d").date()
                except ValueError:
                    errors.append({"index": i, "original": item, "reason": f"日期格式错误 '{bill_date_str}'"})
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
            errors.append({"index": i, "original": item, "reason": f"处理失败: {str(e)}"})

    db.commit()
    return {"success": success, "errors": errors}
