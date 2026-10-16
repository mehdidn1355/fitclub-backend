from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from pathlib import Path
import uuid
import os
import shutil

from app.auth.dependencies import require_trainer
from app.models.user import User

router = APIRouter(prefix="/api", tags=["Upload"])

# پوشه‌ی آپلود
UPLOAD_DIR = Path("uploads/videos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# حداکثر حجم: 500 MB
MAX_FILE_SIZE = 500 * 1024 * 1024

# فرمت‌های مجاز
ALLOWED_EXTENSIONS = {".mp4", ".webm", ".mov", ".avi", ".mkv"}
ALLOWED_MIME_TYPES = {
    "video/mp4",
    "video/webm",
    "video/quicktime",
    "video/x-msvideo",
    "video/x-matroska",
}


@router.post("/upload/video")
async def upload_video(
    file: UploadFile = File(...),
    current_user: User = Depends(require_trainer),
):
    """آپلود ویدئو (فقط مربی و ادمین)."""
    # چک فرمت
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"فرمت مجاز: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="نوع فایل مجاز نیست",
        )

    # چک حجم
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"حجم فایل نباید بیشتر از {MAX_FILE_SIZE // (1024*1024)} MB باشه",
        )

    # نام فایل یکتا
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / unique_name

    # ذخیره
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در ذخیره: {e}")

    return {
        "filename": unique_name,
        "url": f"/api/videos/{unique_name}",
        "size": size,
        "original_name": file.filename,
    }


@router.get("/videos/{filename}")
async def get_video(filename: str):
    """پخش ویدئو."""
    # جلوگیری از path traversal
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="نام فایل نامعتبر")

    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="ویدئو یافت نشد")

    return FileResponse(
        path=file_path,
        media_type="video/mp4",
        headers={"Accept-Ranges": "bytes"},
    )


@router.delete("/videos/{filename}")
async def delete_video(
    filename: str,
    current_user: User = Depends(require_trainer),
):
    """حذف ویدئو (فقط مربی)."""
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="نام فایل نامعتبر")

    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="ویدئو یافت نشد")

    file_path.unlink()
    return {"message": "ویدئو حذف شد"}