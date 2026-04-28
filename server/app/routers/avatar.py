import os
import uuid
import logging
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from fastapi.responses import FileResponse

from app.auth import update_user_profile, get_user_by_id
from app.dependencies import require_auth, require_admin

logger = logging.getLogger("avatar")

router = APIRouter(prefix="/api/v1/avatar", tags=["头像管理"], dependencies=[Depends(require_auth)])

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "avatars"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE = 2 * 1024 * 1024


@router.post("/upload", summary="上传头像")
async def upload_avatar(
    file: UploadFile = File(...),
    user_id: int = Depends(require_admin),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="仅支持 JPG、PNG、WebP 格式的图片")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="图片大小不能超过 2MB")

    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else "jpg"
    if ext not in ("jpg", "jpeg", "png", "webp"):
        ext = "jpg"

    filename = f"{user_id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = UPLOAD_DIR / filename

    for old_file in UPLOAD_DIR.glob(f"{user_id}_*"):
        old_file.unlink(missing_ok=True)

    with open(filepath, "wb") as f:
        f.write(content)

    avatar_url = f"/api/v1/avatar/file/{filename}"
    success, msg = update_user_profile(user_id, avatar=avatar_url)
    if not success:
        raise HTTPException(status_code=400, detail=msg)

    logger.info(f"用户 {user_id} 上传头像: {filename}")
    return {
        "code": 200,
        "message": "头像上传成功",
        "data": {"avatar": avatar_url},
    }


@router.get("/file/{filename}", summary="获取头像文件")
def get_avatar_file(filename: str):
    filepath = UPLOAD_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="头像文件不存在")
    return FileResponse(filepath, media_type="image/jpeg")
