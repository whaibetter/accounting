"""
分类API路由模块。

功能描述：
    提供分类的增删改查接口，支持：
    - 获取分类树（按类型筛选）
    - 创建新分类（支持二级分类）
    - 更新分类信息
    - 删除分类

接口列表：
    GET    /api/v1/categories          获取分类树
    POST   /api/v1/categories          创建分类
    PUT    /api/v1/categories/{id}     更新分类
    DELETE /api/v1/categories/{id}     删除分类

分类结构说明：
    分类采用二级结构，顶级分类通过parent_id=None标识，
    子分类的parent_id指向父分类ID。获取分类树时返回嵌套结构。

异常处理：
    - 404: 分类不存在
    - 400: 存在子分类或关联账单时无法删除
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/api/v1/categories", tags=["分类管理"])


@router.get("", response_model=schemas.ApiResponse[list[schemas.CategoryOut]],
            summary="获取分类树")
def list_categories(
    type: Optional[int] = Query(None, ge=1, le=2, description="类型: 1-支出 2-收入"),
    db: Session = Depends(get_db),
):
    """
    获取分类树结构。

    返回顶级分类列表，每个顶级分类包含其子分类列表。
    可通过type参数筛选支出或收入分类。

    Args:
        type: 类型筛选 (1-支出, 2-收入, 不传则返回全部)

    Returns:
        ApiResponse[List[CategoryOut]]: 分类树列表
    """
    categories = crud.get_categories(db, type_=type)

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
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    """
    创建新分类。

    如果指定parent_id，则创建子分类，类型自动继承父分类。

    Args:
        category: 分类创建请求体

    Returns:
        ApiResponse[CategoryOut]: 新创建的分类信息

    Raises:
        HTTPException 400: 父分类不存在
    """
    try:
        new_cat = crud.create_category(
            db, name=category.name, type_=category.type,
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
                    db: Session = Depends(get_db)):
    """
    更新分类信息。

    Args:
        category_id: 分类ID
        category: 分类更新请求体

    Returns:
        ApiResponse[CategoryOut]: 更新后的分类信息

    Raises:
        HTTPException 404: 分类不存在
    """
    try:
        data = category.model_dump(exclude_unset=True)
        updated = crud.update_category(db, category_id, **data)
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
                    db: Session = Depends(get_db)):
    """
    删除分类。

    默认情况下，如果分类下存在子分类或关联账单记录，则不允许删除。
    当cascade=True时，将级联删除所有子分类（子分类下有账单时仍会阻止）。

    Args:
        category_id: 分类ID
        cascade: 是否级联删除子分类

    Returns:
        ApiResponse[None]: 删除结果

    Raises:
        HTTPException 404: 分类不存在
        HTTPException 400: 存在子分类或关联账单
    """
    try:
        if not crud.delete_category(db, category_id, cascade=cascade):
            raise HTTPException(status_code=404, detail="分类不存在")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return schemas.ApiResponse(message="删除成功")
