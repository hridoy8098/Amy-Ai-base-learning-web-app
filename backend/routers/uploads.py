from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from core.security import get_current_user, get_current_admin
from core.config import UPLOAD_DIR, MAX_UPLOAD_SIZE, ALLOWED_IMAGE_TYPES, ALLOWED_DOC_TYPES, ALLOWED_VIDEO_TYPES
from models.models import User
from sqlalchemy.orm import Session
from core.database import get_db
import os, uuid, aiofiles

router = APIRouter()

for sub in ["avatars","thumbnails","videos","docs","certificates"]:
    os.makedirs(os.path.join(UPLOAD_DIR, sub), exist_ok=True)


async def _save(file: UploadFile, subdir: str, allowed: set) -> str:
    if file.content_type not in allowed:
        raise HTTPException(400, f"File type {file.content_type} not allowed")
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(400, "File too large")
    ext = os.path.splitext(file.filename or "file")[1].lower()
    fname = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, subdir, fname)
    async with aiofiles.open(path, "wb") as f:
        await f.write(content)
    return f"/uploads/{subdir}/{fname}"


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    url = await _save(file, "avatars", ALLOWED_IMAGE_TYPES)
    if user.avatar and user.avatar.startswith("/uploads/"):
        old = user.avatar.lstrip("/")
        if os.path.exists(old): os.remove(old)
    user.avatar = url; db.commit()
    return {"url": url, "message": "Avatar updated"}


@router.post("/thumbnail")
async def upload_thumbnail(file: UploadFile = File(...), admin=Depends(get_current_admin)):
    return {"url": await _save(file, "thumbnails", ALLOWED_IMAGE_TYPES)}


@router.post("/video")
async def upload_video(file: UploadFile = File(...), admin=Depends(get_current_admin)):
    return {"url": await _save(file, "videos", ALLOWED_VIDEO_TYPES)}


@router.post("/document")
async def upload_document(file: UploadFile = File(...), admin=Depends(get_current_admin)):
    url = await _save(file, "docs", ALLOWED_DOC_TYPES)
    return {"url": url, "filename": file.filename}
