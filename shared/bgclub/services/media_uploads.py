from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

MAX_IMAGE_BYTES = 5 * 1024 * 1024


class MediaUploadError(Exception):
    def __init__(self, message: str, code: str = "upload_error") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


def ensure_upload_dirs(upload_root: Path) -> Path:
    announcements_dir = upload_root / "announcements"
    announcements_dir.mkdir(parents=True, exist_ok=True)
    return announcements_dir


async def save_announcement_image(upload_root: Path, file: UploadFile) -> str:
    content_type = (file.content_type or "").lower()
    extension = ALLOWED_IMAGE_TYPES.get(content_type)
    if extension is None:
        raise MediaUploadError(
            "Допустимы только JPEG, PNG, WebP и GIF",
            "invalid_type",
        )

    content = await file.read()
    if not content:
        raise MediaUploadError("Файл пустой", "empty_file")
    if len(content) > MAX_IMAGE_BYTES:
        raise MediaUploadError("Максимальный размер файла — 5 МБ", "file_too_large")

    announcements_dir = ensure_upload_dirs(upload_root)
    filename = f"{uuid4().hex}{extension}"
    target = announcements_dir / filename
    target.write_bytes(content)

    return f"/uploads/announcements/{filename}"
