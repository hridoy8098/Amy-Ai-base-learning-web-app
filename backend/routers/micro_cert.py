"""
Feature #26 — Micro-Certification
ছোট skill-এর badge — LinkedIn-এ share করা যাবে।
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from models.models import User, QuizResult, AmyMessage, MicroCertificate
import uuid
from datetime import datetime

router = APIRouter()

MICRO_SKILLS = [
    {"id": "grammar_basics",    "name": "Grammar Basics",        "icon": "✏️",  "requirement": "Score 80%+ on 3 grammar quizzes",    "xp_needed": 100},
    {"id": "business_english",  "name": "Business English",      "icon": "💼", "requirement": "Complete Business English module",    "xp_needed": 300},
    {"id": "speaking_beginner", "name": "Speaking: Beginner",    "icon": "🎤", "requirement": "Complete 10 voice sessions",          "xp_needed": 150},
    {"id": "speaking_intermediate","name":"Speaking: Intermediate","icon":"🗣️","requirement": "Complete 30 voice sessions with 70%+ fluency","xp_needed": 500},
    {"id": "vocabulary_100",    "name": "Vocabulary Master 100", "icon": "📖", "requirement": "Save 100 vocabulary words",           "xp_needed": 200},
    {"id": "quiz_master",       "name": "Quiz Champion",         "icon": "🏆", "requirement": "Score 90%+ on 10 quizzes",           "xp_needed": 400},
    {"id": "ielts_ready",       "name": "IELTS Ready",           "icon": "🎓", "requirement": "Complete IELTS preparation course",  "xp_needed": 1000},
    {"id": "streak_30",         "name": "30-Day Streak",         "icon": "🔥", "requirement": "Maintain a 30-day learning streak",  "xp_needed": 600},
    {"id": "it_english",        "name": "IT English Pro",        "icon": "💻", "requirement": "Complete IT English module",         "xp_needed": 350},
    {"id": "fluency_advanced",  "name": "Advanced Fluency",      "icon": "⭐", "requirement": "Achieve 80+ fluency score consistently","xp_needed": 800},
]

@router.get("/skills")
def get_skills():
    return MICRO_SKILLS

@router.get("/my-certs")
def get_my_certs(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    certs = db.query(MicroCertificate).filter(MicroCertificate.user_id == user.id).all()
    return [{"id": c.id, "skill_id": c.skill_id, "skill_name": c.skill_name, "cert_code": c.cert_code, "issued_at": c.issued_at.isoformat(), "share_url": c.share_url} for c in certs]

@router.get("/eligible")
def get_eligible(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    already = {c.skill_id for c in db.query(MicroCertificate).filter(MicroCertificate.user_id == user.id).all()}
    eligible = []
    for skill in MICRO_SKILLS:
        if skill["id"] not in already and user.xp_points >= skill["xp_needed"]:
            eligible.append(skill)
    return eligible

@router.post("/claim/{skill_id}")
def claim_cert(skill_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    skill = next((s for s in MICRO_SKILLS if s["id"] == skill_id), None)
    if not skill: raise HTTPException(404, "Skill not found")
    if user.xp_points < skill["xp_needed"]:
        raise HTTPException(403, f"Need {skill['xp_needed']} XP to claim this certificate. You have {user.xp_points} XP.")
    existing = db.query(MicroCertificate).filter(MicroCertificate.user_id == user.id, MicroCertificate.skill_id == skill_id).first()
    if existing: return {"message": "Already claimed!", "cert_code": existing.cert_code}
    cert_code = f"AMY-MICRO-{uuid.uuid4().hex[:8].upper()}"
    share_url = f"/verify/{cert_code}"
    cert = MicroCertificate(user_id=user.id, skill_id=skill_id, skill_name=skill["name"], cert_code=cert_code, share_url=share_url)
    db.add(cert); db.commit(); db.refresh(cert)
    return {"message": f"🎉 Congratulations! You earned '{skill['name']}' certificate!", "cert_code": cert_code, "share_url": share_url, "linkedin_text": f"I just earned the '{skill['name']}' micro-certificate on Amy Learning Platform! #EnglishLearning #AmyLearn"}

@router.get("/verify/{cert_code}")
def verify_cert(cert_code: str, db: Session = Depends(get_db)):
    cert = db.query(MicroCertificate).filter(MicroCertificate.cert_code == cert_code).first()
    if not cert: raise HTTPException(404, "Certificate not found")
    user = db.query(User).filter(User.id == cert.user_id).first()
    return {"valid": True, "cert_code": cert_code, "skill_name": cert.skill_name, "earner_name": user.name if user else "Unknown", "issued_at": cert.issued_at.isoformat()}