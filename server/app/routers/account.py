from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, schemas
from app.dependencies import require_auth

router = APIRouter(prefix="/api/v1/accounts", tags=["账户管理"], dependencies=[Depends(require_auth)])


@router.get("", response_model=schemas.ApiResponse[list[schemas.AccountOut]],
            summary="获取账户列表")
def list_accounts(user_id: int = Depends(require_auth), db: Session = Depends(get_db)):
    accounts = crud.get_accounts(db, user_id)
    return schemas.ApiResponse(data=[schemas.AccountOut.model_validate(a) for a in accounts])


@router.post("", response_model=schemas.ApiResponse[schemas.AccountOut],
             summary="创建账户")
def create_account(account: schemas.AccountCreate, user_id: int = Depends(require_auth), db: Session = Depends(get_db)):
    new_account = crud.create_account(
        db, user_id=user_id, name=account.name, type_=account.type, icon=account.icon,
        color=account.color, initial_balance=account.initial_balance,
        is_default=account.is_default,
    )
    return schemas.ApiResponse(data=schemas.AccountOut.model_validate(new_account))


@router.get("/{account_id}", response_model=schemas.ApiResponse[schemas.AccountOut],
            summary="获取账户详情")
def get_account(account_id: int, user_id: int = Depends(require_auth), db: Session = Depends(get_db)):
    account = crud.get_account(db, account_id, user_id)
    if not account:
        raise HTTPException(status_code=404, detail="账户不存在")
    return schemas.ApiResponse(data=schemas.AccountOut.model_validate(account))


@router.put("/{account_id}", response_model=schemas.ApiResponse[schemas.AccountOut],
            summary="更新账户")
def update_account(account_id: int, account: schemas.AccountUpdate,
                   user_id: int = Depends(require_auth), db: Session = Depends(get_db)):
    updated = crud.update_account(db, account_id, user_id, **account.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail="账户不存在")
    return schemas.ApiResponse(data=schemas.AccountOut.model_validate(updated))


@router.delete("/{account_id}", response_model=schemas.ApiResponse[None],
               summary="删除账户")
def delete_account(account_id: int, user_id: int = Depends(require_auth), db: Session = Depends(get_db)):
    try:
        if not crud.delete_account(db, account_id, user_id):
            raise HTTPException(status_code=404, detail="账户不存在")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return schemas.ApiResponse(message="删除成功")
