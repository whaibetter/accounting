from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app import crud, schemas
from app.dependencies import require_auth

router = APIRouter(prefix="/api/v1/categories", tags=["分类管理"], dependencies=[Depends(require_auth)])


@router.get("", response_model=schemas.ApiResponse[list[schemas.CategoryOut]],
            summary="获取分类树")
def list_categories(
    type: Optional[int] = Query(None, ge=1, le=2, description="类型: 1-支出 2-收入"),
    user_id: int = Depends(require_auth),
    db: Session = Depends(get_db),
):
    categories = crud.get_categories(db, user_id, type_=type)

    def to_out(cat):
        return schemas.CategoryOut(
            id=cat.id,
            parent_id=cat.parent_id,
            name=cat.name,
            type=cat.type,
            icon=cat.icon,
            sort_order=cat.sort_order,
            children=[to_out(c) for c in cat.children] if cat.children else [],
        )

    return schemas.ApiResponse(data=[to_out(c) for c in categories])


@router.post("", response_model=schemas.ApiResponse[schemas.CategoryOut],
             summary="创建分类")
def create_category(category: schemas.CategoryCreate, user_id: int = Depends(require_auth), db: Session = Depends(get_db)):
    try:
        new_cat = crud.create_category(
            db, user_id, name=category.name, type_=category.type,
            parent_id=category.parent_id, icon=category.icon,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return schemas.ApiResponse(data=schemas.CategoryOut(
        id=new_cat.id, parent_id=new_cat.parent_id, name=new_cat.name,
        type=new_cat.type, icon=new_cat.icon, sort_order=new_cat.sort_order,
        children=[],
    ))


@router.put("/{category_id}", response_model=schemas.ApiResponse[schemas.CategoryOut],
            summary="更新分类")
def update_category(category_id: int, category: schemas.CategoryUpdate,
                    user_id: int = Depends(require_auth), db: Session = Depends(get_db)):
    try:
        data = category.model_dump(exclude_unset=True)
        updated = crud.update_category(db, category_id, user_id, **data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not updated:
        raise HTTPException(status_code=404, detail="分类不存在")

    return schemas.ApiResponse(data=schemas.CategoryOut(
        id=updated.id, parent_id=updated.parent_id, name=updated.name,
        type=updated.type, icon=updated.icon, sort_order=updated.sort_order,
        children=[],
    ))


@router.delete("/{category_id}", response_model=schemas.ApiResponse[None],
               summary="删除分类")
def delete_category(category_id: int, cascade: bool = Query(False, description="是否级联删除子分类"),
                    user_id: int = Depends(require_auth), db: Session = Depends(get_db)):
    try:
        if not crud.delete_category(db, category_id, user_id, cascade=cascade):
            raise HTTPException(status_code=404, detail="分类不存在")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return schemas.ApiResponse(message="删除成功")
