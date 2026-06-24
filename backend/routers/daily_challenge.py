"""
Feature #8 — Daily Challenge System
প্রতিদিন specific challenge — complete করলে bonus XP + badge।
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from core.database import get_db, Base
from core.security import get_current_user
from core.ai_providers import call_ai
from models.models import User
from datetime import datetime, date
import json, re, hashlib

router = APIRouter()

DAILY_CHALLENGES = [
    {"id": 1, "type": "vocabulary",  "icon": "📖", "title": "Word of the Day",      "description": "Learn and use 3 new vocabulary words in sentences.",    "xp": 20},
    {"id": 2, "type": "grammar",     "icon": "✏️",  "title": "Grammar Fix",          "description": "Identify and fix grammar errors in 5 sentences.",        "xp": 25},
    {"id": 3, "type": "speaking",    "icon": "🎤", "title": "Speaking Challenge",    "description": "Have a 5-minute conversation with Amy about any topic.",  "xp": 30},
    {"id": 4, "type": "quiz",        "icon": "🧠", "title": "Quick Quiz",           "description": "Complete a 10-question quiz with 70%+ score.",            "xp": 35},
    {"id": 5, "type": "reading",     "icon": "📰", "title": "Read & Summarize",     "description": "Read a passage and summarize it in your own words.",      "xp": 25},
    {"id": 6, "type": "writing",     "icon": "📝", "title": "Write a Paragraph",    "description": "Write a 100-word paragraph on today's topic.",            "xp": 30},
    {"id": 7, "type": "roleplay",    "icon": "🎭", "title": "Roleplay Scenario",    "description": "Practice a real-life English scenario with Amy.",         "xp": 40},
]

def get_today_challenge():
    day_num = (date.today() - date(2025, 1, 1)).days
    return DAILY_CHALLENGES[day_num % len(DAILY_CHALLENGES)]

@router.get("/today")
def get_daily_challenge(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    challenge = get_today_challenge()
    today_str = date.today().isoformat()
    # Check completion via xp reset date as proxy (simplified)
    return {
        "challenge": challenge,
        "date": today_str,
        "completed": False,
        "streak": user.streak_days,
    }

@router.post("/complete")
def complete_challenge(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    challenge = get_today_challenge()
    xp = challenge["xp"]
    user.xp_points += xp
    # Update streak
    today = date.today()
    last = user.last_active.date() if user.last_active else None
    if last == today:
        pass
    elif last and (today - last).days == 1:
        user.streak_days = (user.streak_days or 0) + 1
    else:
        user.streak_days = 1
    user.last_active = datetime.utcnow()
    db.commit()
    return {"message": "Challenge completed!", "xp_earned": xp, "total_xp": user.xp_points, "streak": user.streak_days}

@router.get("/history")
def challenge_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"completed_count": 0, "current_streak": user.streak_days, "total_xp_from_challenges": 0}
