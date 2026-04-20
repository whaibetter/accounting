"""
标签API路由模块。

功能描述：
    提供标签的增删改查接口，支持：
    - 获取标签列表
    - 创建新标签
    - 更新标签信息
    - 删除标签

接口列表：
    GET    /api/v1/tags          获取标签列表
    POST   /api/v1/tags          创建标签
    PUT    /api/v1/tags/{id}     更新标签
    DELETE /api/v1/tags/{id}     删除标签

异常处理：
    - 404: 标签不存在
    - 400: 标签名称已存在
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/api/v1/tags", tags=["标签管理"])


@router.get("", response_model=schemas.ApiResponse[list[schemas.TagOut]],
            summary="获取标签列表")
def list_tags(db: Session = Depends(get_db)):
    """
    获取所有标签列表。

    Returns:
        ApiResponse[List[TagOut]]: 标签列表
    """
    tags = crud.get_tags(db)
    return schemas.ApiResponse(data=[schemas.TagOut.model_validate(t) for t in tags])


@router.post("", response_model=schemas.ApiResponse[schemas.TagOut],
             summary="创建标签")
def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db)):
    """
    创建新标签。

    标签名称必须唯一，重复名称会返回400错误。

    Args:
        tag: 标签创建请求体

    Returns:
        ApiResponse[TagOut]: 新创建的标签信息

    Raises:
        HTTPException 400: 标签名称已存在
    """
    try:
        new_tag = crud.create_tag(db, name=tag.name, color=tag.color)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return schemas.ApiResponse(data=schemas.TagOut.model_validate(new_tag))


@router.put("/{tag_id}", response_model=schemas.ApiResponse[schemas.TagOut],
            summary="更新标签")
def update_tag(tag_id: int, tag: schemas.TagUpdate, db: Session = Depends(get_db)):
    """
    更新标签信息。

    Args:
        tag_id: 标签ID
        tag: 标签更新请求体

    Returns:
        ApiResponse[TagOut]: 更新后的标签信息

    Raises:
        HTTPException 404: 标签不存在
    """
    updated = crud.update_tag(db, tag_id, **tag.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail="标签不存在")
    return schemas.ApiResponse(data=schemas.TagOut.model_validate(updated))


@router.delete("/{tag_id}", response_model=schemas.ApiResponse[None],
               summary="删除标签")
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """
    删除标签。

    删除标签时会同时删除该标签与所有账单的关联关系。

    Args:
        tag_id: 标签ID

    Returns:
        ApiResponse[None]: 删除结果

    Raises:
        HTTPException 404: 标签不存在
    """
    if not crud.delete_tag(db, tag_id):
        raise HTTPException(status_code=404, detail="标签不存在")
    return schemas.ApiResponse(message="删除成功")
