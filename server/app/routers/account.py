"""
资金账户API路由模块。

功能描述：
    提供资金账户的增删改查接口，支持：
    - 获取账户列表
    - 创建新账户
    - 获取单个账户详情
    - 更新账户信息
    - 删除账户

接口列表：
    GET    /api/v1/accounts          获取账户列表
    POST   /api/v1/accounts          创建账户
    GET    /api/v1/accounts/{id}     获取账户详情
    PUT    /api/v1/accounts/{id}     更新账户
    DELETE /api/v1/accounts/{id}     删除账户

异常处理：
    - 404: 账户不存在
    - 400: 账户下存在账单记录无法删除
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/api/v1/accounts", tags=["账户管理"])


@router.get("", response_model=schemas.ApiResponse[list[schemas.AccountOut]],
            summary="获取账户列表")
def list_accounts(db: Session = Depends(get_db)):
    """
    获取所有资金账户列表。

    返回按排序序号排列的所有账户，包括已归档的账户。

    Returns:
        ApiResponse[List[AccountOut]]: 账户列表
    """
    accounts = crud.get_accounts(db)
    return schemas.ApiResponse(data=[schemas.AccountOut.model_validate(a) for a in accounts])


@router.post("", response_model=schemas.ApiResponse[schemas.AccountOut],
             summary="创建账户")
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    """
    创建新的资金账户。

    如果设为默认账户，会自动取消其他账户的默认状态。
    账户余额初始化为initial_balance。

    Args:
        account: 账户创建请求体

    Returns:
        ApiResponse[AccountOut]: 新创建的账户信息
    """
    new_account = crud.create_account(
        db, name=account.name, type_=account.type, icon=account.icon,
        color=account.color, initial_balance=account.initial_balance,
        is_default=account.is_default,
    )
    return schemas.ApiResponse(data=schemas.AccountOut.model_validate(new_account))


@router.get("/{account_id}", response_model=schemas.ApiResponse[schemas.AccountOut],
            summary="获取账户详情")
def get_account(account_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取单个账户的详细信息。

    Args:
        account_id: 账户ID

    Returns:
        ApiResponse[AccountOut]: 账户详情

    Raises:
        HTTPException 404: 账户不存在
    """
    account = crud.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="账户不存在")
    return schemas.ApiResponse(data=schemas.AccountOut.model_validate(account))


@router.put("/{account_id}", response_model=schemas.ApiResponse[schemas.AccountOut],
            summary="更新账户")
def update_account(account_id: int, account: schemas.AccountUpdate,
                   db: Session = Depends(get_db)):
    """
    更新账户信息。

    仅更新请求体中提供的非None字段。

    Args:
        account_id: 账户ID
        account: 账户更新请求体

    Returns:
        ApiResponse[AccountOut]: 更新后的账户信息

    Raises:
        HTTPException 404: 账户不存在
    """
    updated = crud.update_account(db, account_id, **account.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail="账户不存在")
    return schemas.ApiResponse(data=schemas.AccountOut.model_validate(updated))


@router.delete("/{account_id}", response_model=schemas.ApiResponse[None],
               summary="删除账户")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    """
    删除资金账户。

    如果账户下存在账单记录，则不允许删除。

    Args:
        account_id: 账户ID

    Returns:
        ApiResponse[None]: 删除结果

    Raises:
        HTTPException 404: 账户不存在
        HTTPException 400: 账户下存在账单记录
    """
    try:
        if not crud.delete_account(db, account_id):
            raise HTTPException(status_code=404, detail="账户不存在")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return schemas.ApiResponse(message="删除成功")
