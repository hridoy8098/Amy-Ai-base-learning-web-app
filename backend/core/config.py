from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

APP_NAME        = os.getenv("APP_NAME", "Amy Learning")
FRONTEND_URL    = os.getenv("FRONTEND_URL", "http://localhost:5173")
_raw_upload_dir = os.getenv("UPLOAD_DIR", "uploads")
_upload_path = Path(_raw_upload_dir)
if not _upload_path.is_absolute():
    _upload_path = BASE_DIR / _upload_path
UPLOAD_DIR      = str(_upload_path.resolve())
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 52428800))  # 50MB

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_DOC_TYPES   = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/ogg"}

ADMIN_EMAIL    = os.getenv("ADMIN_EMAIL", "admin@amy.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_NAME     = os.getenv("ADMIN_NAME", "Admin")

# Amy usage limits for different plans
AMY_FREE_DAILY_LIMIT  = 10
AMY_FREE_VOICE_LIMIT  = 5

# Quiz limits by subscription plan
QUIZ_LIMITS = {
    "free": {
        "daily": 3,
        "weekly": 10,
        "monthly": 25,
    },
    "basic": {
        "daily": 15,
        "weekly": 50,
        "monthly": 200,
    },
    "pro": {
        "daily": 30,
        "weekly": 100,
        "monthly": 500,
    },
    "premium": {
        "daily": None,      # Unlimited
        "weekly": None,     # Unlimited
        "monthly": None,    # Unlimited
    },
}
