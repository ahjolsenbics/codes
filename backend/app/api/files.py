"""证件与货物照片上传。Demo 落本地磁盘，接口形态对齐 OSS。"""

from fastapi import APIRouter, Depends, File, UploadFile

from app.core.storage import save_upload
from app.deps import get_current_user
from app.models import User

router = APIRouter()


@router.post("/files")
async def upload_file(file: UploadFile = File(...), user: User = Depends(get_current_user)) -> dict:
    return await save_upload(file, owner_id=user.id)
