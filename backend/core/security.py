from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core.database import get_db
import os
from pathlib import Path
from dotenv import load_dotenv

# 🔥 Load .env
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

# 🔐 Config
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-this")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 10080))

# 🔒 Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔑 Auth scheme
bearer = HTTPBearer()

# =========================
# 🔐 PASSWORD FUNCTIONS
# =========================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# =========================
# 🔐 TOKEN CREATE
# =========================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    # 🔥 FIX: sub MUST be string
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])

    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# =========================
# 🔐 TOKEN DECODE
# =========================

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

# =========================
# 👤 CURRENT USER
# =========================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
):
    from models.models import User

    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials

        payload = decode_token(token)

        # 🔥 FIX: safe sub extraction
        sub = payload.get("sub")
        if sub is None:
            raise exc

        user_id = int(sub)

    except JWTError:
        raise exc
    except Exception:
        raise exc

    user = db.query(User).filter(
        User.id == user_id,
        User.is_active == True
    ).first()

    if not user:
        raise exc

    return user

# =========================
# 👑 ADMIN CHECK
# =========================

def get_current_admin(user=Depends(get_current_user)):
    if user.role not in ("admin", "superadmin"):
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return user

# =========================
# 👤 OPTIONAL USER
# =========================

def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: Session = Depends(get_db),
):
    if not credentials:
        return None

    try:
        from models.models import User

        payload = decode_token(credentials.credentials)

        sub = payload.get("sub")
        if not sub:
            return None

        user_id = int(sub)

        return db.query(User).filter(
            User.id == user_id,
            User.is_active == True
        ).first()

    except Exception:
        return None
