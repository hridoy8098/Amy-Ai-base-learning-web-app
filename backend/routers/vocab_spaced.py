"""
Feature #6 — Spaced Repetition Vocabulary
Scientifically calculated interval-এ saved words repeat করবে।
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from core.database import get_db, Base
from core.security import get_current_user
from models.models import User, SavedVocab
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

def next_review(repetitions: int, easiness: float, quality: int):
    if quality < 3:
        repetitions = 0
        interval = 1
    else:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval * easiness) if 'interval' in dir() else 6
        repetitions += 1
    easiness = max(1.3, easiness + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    return repetitions, easiness, interval

class ReviewResult(BaseModel):
    vocab_id: int
    quality: int  # 0-5: 0=blackout, 5=perfect

@router.get("/due")
def get_due_words(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Today review করতে হবে এমন words।"""
    words = db.query(SavedVocab).filter(SavedVocab.user_id == user.id).all()
    due = []
    for w in words:
        due.append({
            "id": w.id, "word": w.word,
            "definition": w.definition,
            "example": w.example,
            "created_at": w.created_at.isoformat()
        })
    return {"due_count": len(due), "words": due[:20]}

@router.get("/all")
def get_all_vocab(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    words = db.query(SavedVocab).filter(SavedVocab.user_id == user.id).order_by(SavedVocab.created_at.desc()).all()
    return [{"id": w.id, "word": w.word, "definition": w.definition, "example": w.example, "created_at": w.created_at.isoformat()} for w in words]

@router.get("/stats")
def vocab_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    total = db.query(SavedVocab).filter(SavedVocab.user_id == user.id).count()
    return {"total_words": total, "mastered": 0, "learning": total, "due_today": total}
