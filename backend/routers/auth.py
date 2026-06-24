from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from core.database import get_db
from core.security import (
    hash_password, verify_password,
    create_access_token, get_current_user
)
from models.models import User
from datetime import datetime
import secrets, string

router = APIRouter()

# ── Schemas ───────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    referral_code: str = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class UpdateProfileRequest(BaseModel):
    name: str = None
    bio:  str = None
    email: EmailStr = None

# ── Helpers ───────────────────────────────────────────────────────

def _gen_code(n=8):
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(n))

def _user_dict(u: User) -> dict:
    return {
        "id":            u.id,
        "name":          u.name,
        "email":         u.email,
        "avatar":        u.avatar,
        "bio":           u.bio,
        "role":          u.role,
        "is_active":     u.is_active,
        "is_verified":   u.is_verified,
        "subscription_plan":    u.subscription_plan,
        "subscription_expires": u.subscription_expires.isoformat() if u.subscription_expires else None,
        "xp_points":     u.xp_points,
        "streak_days":   u.streak_days,
        "level":         u.level,
        "referral_code": u.referral_code,
        "created_at":    u.created_at.isoformat() if u.created_at else None,
    }

def _update_level(u: User):
    thresholds = [0,100,300,600,1000,1500,2200,3000,4000,5500,7500]
    for i, t in enumerate(thresholds):
        if u.xp_points >= t:
            u.level = i + 1

# ── Routes ────────────────────────────────────────────────────────

@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(400, "Email already registered")
    if len(req.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")

    referred_by = None
    if req.referral_code:
        referrer = db.query(User).filter(User.referral_code == req.referral_code).first()
        if referrer:
            referred_by = referrer.id
            referrer.xp_points += 50

    user = User(
        name=req.name.strip(),
        email=req.email.lower(),
        password_hash=hash_password(req.password),
        referral_code=_gen_code(),
        referred_by=referred_by,
    )
    db.add(user); db.commit(); db.refresh(user)
    token = create_access_token({"sub": user.id, "role": user.role})
    return {"token": token, "user": _user_dict(user)}


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    if not user.is_active:
        raise HTTPException(403, "Account is disabled")

    now = datetime.utcnow()
    if user.last_active:
        diff = (now.date() - user.last_active.date()).days
        if diff == 1:   user.streak_days += 1
        elif diff > 1:  user.streak_days = 1
    else:
        user.streak_days = 1
    user.last_active = now
    db.commit()

    token = create_access_token({"sub": user.id, "role": user.role})
    return {"token": token, "user": _user_dict(user)}


@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return _user_dict(user)


@router.put("/profile")
def update_profile(
    req: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if req.name:  user.name = req.name.strip()
    if req.bio is not None: user.bio = req.bio
    if req.email and req.email != user.email:
        if db.query(User).filter(User.email == req.email, User.id != user.id).first():
            raise HTTPException(400, "Email already in use")
        user.email = req.email.lower()
    db.commit(); db.refresh(user)
    return {"message": "Profile updated", "user": _user_dict(user)}


@router.post("/change-password")
def change_password(
    req: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(req.current_password, user.password_hash):
        raise HTTPException(400, "Current password is incorrect")
    if len(req.new_password) < 6:
        raise HTTPException(400, "New password must be at least 6 characters")
    user.password_hash = hash_password(req.new_password)
    db.commit()
    return {"message": "Password changed successfully"}


@router.get("/stats")
def get_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from models.models import Enrollment, QuizResult, AmyMessage, UserBadge, Certificate

    return {
        "xp_points":        user.xp_points,
        "streak_days":      user.streak_days,
        "level":            user.level,
        "enrolled_courses": db.query(Enrollment).filter(Enrollment.user_id == user.id).count(),
        "completed_courses":db.query(Enrollment).filter(Enrollment.user_id == user.id, Enrollment.completed == True).count(),
        "quiz_taken":       db.query(QuizResult).filter(QuizResult.user_id == user.id).count(),
        "amy_messages":     db.query(AmyMessage).filter(AmyMessage.user_id == user.id, AmyMessage.role == "user").count(),
        "badges_earned":    db.query(UserBadge).filter(UserBadge.user_id == user.id).count(),
        "certificates":     db.query(Certificate).filter(Certificate.user_id == user.id).count(),
        "subscription":     user.subscription_plan,
    }
