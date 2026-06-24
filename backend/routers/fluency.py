"""
Feature #3 — Fluency Score Over Time
প্রতিটা conversation-এর পর score, graph-এ progress দেখা যাবে।
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from models.models import User, AmyMessage, QuizResult, FluencyRecord
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/history")
def fluency_history(days: int = 30, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(days=days)
    records = db.query(FluencyRecord).filter(
        FluencyRecord.user_id == user.id,
        FluencyRecord.created_at >= since
    ).order_by(FluencyRecord.created_at.asc()).all()

    # Also include quiz scores as fluency indicators
    quizzes = db.query(QuizResult).filter(
        QuizResult.user_id == user.id,
        QuizResult.created_at >= since
    ).order_by(QuizResult.created_at.asc()).all()

    chart_data = []
    for r in records:
        chart_data.append({"date": r.created_at.strftime("%Y-%m-%d"), "score": r.score, "type": "conversation"})
    for q in quizzes:
        chart_data.append({"date": q.created_at.strftime("%Y-%m-%d"), "score": q.score, "type": "quiz"})

    chart_data.sort(key=lambda x: x["date"])

    avg = round(sum(r.score for r in records) / len(records), 1) if records else 0
    trend = "improving" if len(records) >= 2 and records[-1].score > records[0].score else "stable"

    return {
        "chart_data": chart_data,
        "average_score": avg,
        "trend": trend,
        "total_sessions": len(records),
        "current_level": user.level,
        "xp": user.xp_points
    }

@router.get("/summary")
def fluency_summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    total = db.query(FluencyRecord).filter(FluencyRecord.user_id == user.id).count()
    latest = db.query(FluencyRecord).filter(FluencyRecord.user_id == user.id).order_by(FluencyRecord.created_at.desc()).first()
    return {
        "latest_score": latest.score if latest else 0,
        "total_sessions": total,
        "streak_days": user.streak_days,
        "level": user.level,
        "xp": user.xp_points
    }