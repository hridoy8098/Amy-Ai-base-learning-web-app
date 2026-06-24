"""
Feature #19 — Smart Reminder System
User কখন active সেই সময়ে personalized notification পাঠাবে।
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from models.models import User, Notification, SmartReminder
from datetime import datetime

router = APIRouter()

class ReminderCreate(BaseModel):
    reminder_time: str   # "08:00"
    days: str = "mon,tue,wed,thu,fri,sat,sun"
    message_type: str = "daily_practice"

REMINDER_MESSAGES = {
    "daily_practice":  "🎯 Time to practice English! Open Amy and keep your streak going!",
    "vocab_review":    "📖 Review your vocabulary! Spaced repetition = better memory!",
    "quiz_time":       "🧠 Quick quiz time! Test your knowledge with Amy!",
    "streak_warning":  "🔥 Don't break your streak! Practice for just 5 minutes!",
    "sleep_recap":     "🌙 Time for your bedtime learning recap with Amy!",
    "challenge":       "⚡ Today's daily challenge is waiting for you!",
}

@router.get("/")
def get_reminders(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    reminders = db.query(SmartReminder).filter(SmartReminder.user_id == user.id).all()
    return [{"id": r.id, "reminder_time": r.reminder_time, "days": r.days.split(","), "message_type": r.message_type, "is_active": r.is_active, "preview_message": REMINDER_MESSAGES.get(r.message_type, "")} for r in reminders]

@router.post("/")
def create_reminder(req: ReminderCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    r = SmartReminder(user_id=user.id, reminder_time=req.reminder_time, days=req.days, message_type=req.message_type)
    db.add(r); db.commit(); db.refresh(r)
    return {"id": r.id, "message": "Reminder created!", "preview": REMINDER_MESSAGES.get(req.message_type, "")}

@router.put("/{rid}/toggle")
def toggle_reminder(rid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    r = db.query(SmartReminder).filter(SmartReminder.id == rid, SmartReminder.user_id == user.id).first()
    if not r:
        from fastapi import HTTPException
        raise HTTPException(404, "Not found")
    r.is_active = not r.is_active
    db.commit()
    return {"is_active": r.is_active}

@router.delete("/{rid}")
def delete_reminder(rid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    r = db.query(SmartReminder).filter(SmartReminder.id == rid, SmartReminder.user_id == user.id).first()
    if not r:
        from fastapi import HTTPException
        raise HTTPException(404, "Not found")
    db.delete(r); db.commit()
    return {"message": "Deleted"}

@router.post("/send-now")
def send_test_notification(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notif = Notification(user_id=user.id, title="🎯 Practice Reminder", message=REMINDER_MESSAGES["daily_practice"], type="reminder", link="/amy")
    db.add(notif); db.commit()
    return {"message": "Test notification sent!"}

@router.get("/types")
def get_reminder_types():
    return [{"id": k, "message": v} for k, v in REMINDER_MESSAGES.items()]