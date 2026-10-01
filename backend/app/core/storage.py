"""本地对象存储适配器。生产可换成 OSS/S3，调用方只依赖 save_upload 返回的 url。"""

from __future__ import annotations

import logging
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from app.core.config import settings

logger = logging.getLogger("yunmm")

ALLOWED = {".jpg", ".jpeg", ".png", ".webp"}
MAX_BYTES = 8 * 1024 * 1024


def upload_root() -> Path:
    path = Path(settings.upload_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


async def save_upload(file: UploadFile, *, owner_id: str) -> dict:
    name = (file.filename or "photo.jpg").lower()
    ext = Path(name).suffix
    if ext not in ALLOWED:
        raise HTTPException(status_code=400, detail="仅支持 jpg/png/webp")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="空文件")
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=400, detail="文件超过 8MB")
    fid = uuid4().hex
    dest = upload_root() / f"{fid}{ext}"
    dest.write_bytes(data)
    url = f"/files/{dest.name}"
    logger.info("证件文件已保存 owner=%s file=%s bytes=%s", owner_id, dest.name, len(data))
    return {"id": fid, "url": url, "name": dest.name, "bytes": len(data)}
