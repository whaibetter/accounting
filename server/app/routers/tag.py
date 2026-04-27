from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, schemas
from app.dependencies import require_auth

router = APIRouter(prefix="/api/v1/tags", tags=["标签管理"], dependencies=[Depends(require_auth)])


@router.get("", response_model=schemas.ApiResponse[list[schemas.TagOut]],
            summary="获取标签列表")
def list_tags(user_id: int = Depends(require_auth), db: Session = Depends(get_db)):
    tags = crud.get_tags(db, user_id)
    return schemas.ApiResponse(data=[schemas.TagOut.model_validate(t) for t in tags])


@router.post("", response_model=schemas.ApiResponse[schemas.TagOut],
             summary="创建标签")
def create_tag(tag: schemas.TagCreate, user_id: int = Depends(require_auth), db: Session = Depends(get_db)):
    try:
        new_tag = crud.create_tag(db, user_id, name=tag.name, color=tag.color, icon=tag.icon)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return schemas.ApiResponse(data=schemas.TagOut.model_validate(new_tag))


@router.put("/{tag_id}", response_model=schemas.ApiResponse[schemas.TagOut],
            summary="更新标签")
def update_tag(tag_id: int, tag: schemas.TagUpdate, user_id: int = Depends(require_auth), db: Session = Depends(get_db)):
    updated = crud.update_tag(db, tag_id, user_id, **tag.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail="标签不存在")
    return schemas.ApiResponse(data=schemas.TagOut.model_validate(updated))


@router.delete("/{tag_id}", response_model=schemas.ApiResponse[None],
               summary="删除标签")
def delete_tag(tag_id: int, user_id: int = Depends(require_auth), db: Session = Depends(get_db)):
    if not crud.delete_tag(db, tag_id, user_id):
        raise HTTPException(status_code=404, detail="标签不存在")
    return schemas.ApiResponse(message="删除成功")
