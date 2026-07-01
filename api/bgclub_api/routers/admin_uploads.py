from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from bgclub.config import get_settings
from bgclub.services.media_uploads import MediaUploadError, save_announcement_image
from bgclub_api.deps.auth import require_admin

router = APIRouter(prefix="/admin/uploads", tags=["admin-uploads"])


class UploadOut(BaseModel):
    url: str


@router.post("/announcement-image", response_model=UploadOut)
async def upload_announcement_image(
    file: UploadFile = File(...),
    _admin=Depends(require_admin),
) -> UploadOut:
    settings = get_settings()
    upload_root = Path(settings.upload_dir)
    try:
        url = await save_announcement_image(upload_root, file)
    except MediaUploadError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc
    return UploadOut(url=url)
