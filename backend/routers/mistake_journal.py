"""
Feature #27 — Mistake Journal
Weekly report — কোন grammar ভুল কতবার করেছে।
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from core.database import get_db
from core.security import get_current_user
from core.ai_providers import call_ai
from models.models import User, AmyMessage, QuizResult, GrammarMistake
import json, re
from datetime import datetime, timedelta

router = APIRouter()

class MistakeAdd(BaseModel):
    error_type: str
    original: str
    correction: str
    explanation: Optional[str] = None

@router.get("/")
def get_mistakes(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    mistakes = db.query(GrammarMistake).filter(GrammarMistake.user_id == user.id).order_by(GrammarMistake.count.desc()).all()
    return [{"id": m.id, "error_type": m.error_type, "original": m.original, "correction": m.correction, "explanation": m.explanation, "count": m.count, "last_seen": m.updated_at.isoformat()} for m in mistakes]

@router.post("/add")
def add_mistake(req: MistakeAdd, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(GrammarMistake).filter(GrammarMistake.user_id == user.id, GrammarMistake.original == req.original).first()
    if existing:
        existing.count += 1
        existing.correction = req.correction
    else:
        db.add(GrammarMistake(user_id=user.id, error_type=req.error_type, original=req.original, correction=req.correction, explanation=req.explanation))
    db.commit()
    return {"message": "Mistake logged!"}

@router.get("/weekly-report")
async def weekly_report(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    week_ago = datetime.utcnow() - timedelta(days=7)
    mistakes = db.query(GrammarMistake).filter(GrammarMistake.user_id == user.id, GrammarMistake.updated_at >= week_ago).order_by(GrammarMistake.count.desc()).all()
    quiz_results = db.query(QuizResult).filter(QuizResult.user_id == user.id, QuizResult.created_at >= week_ago).all()

    mistake_data = [{"error_type": m.error_type, "original": m.original, "correction": m.correction, "count": m.count} for m in mistakes[:10]]
    quiz_data = [{"topic": q.topic, "score": q.score} for q in quiz_results]

    system = (
        "You are an English teacher creating a weekly progress report. Return ONLY valid JSON:\n"
        '{"summary":"...","top_mistakes":[{"type":"...","frequency":3,"tip":"..."}],'
        '"improvement_areas":["..."],"achievements":["..."],"weekly_score":75,'
        '"recommended_practice":["..."],"encouragement":"..."}'
    )
    msgs = [{"role": "user", "content": f"Create weekly report. Mistakes: {json.dumps(mistake_data)}. Quiz scores: {json.dumps(quiz_data)}. User: level={user.level}, streak={user.streak_days}"}]

    try:
        raw, provider = await call_ai(system, msgs)
        m = re.search(r'\{.*\}', raw.strip(), re.DOTALL)
        if m: report = json.loads(m.group())
        else: raise ValueError()
    except:
        report = {
            "summary": f"You made {len(mistakes)} grammar mistakes this week.",
            "top_mistakes": [{"type": m.error_type, "frequency": m.count, "tip": f"Review {m.error_type} rules"} for m in mistakes[:3]],
            "improvement_areas": list(set(m.error_type for m in mistakes))[:3],
            "achievements": [f"Completed {len(quiz_results)} quizzes this week"],
            "weekly_score": 70,
            "recommended_practice": ["Review verb tenses", "Practice with Amy daily"],
            "encouragement": "Keep going! Every mistake is a learning opportunity!"
        }

    return {"report": report, "mistake_count": len(mistakes), "quiz_count": len(quiz_results)}

@router.get("/stats")
def mistake_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    mistakes = db.query(GrammarMistake).filter(GrammarMistake.user_id == user.id).all()
    by_type = {}
    for m in mistakes:
        if m.error_type not in by_type: by_type[m.error_type] = 0
        by_type[m.error_type] += m.count
    sorted_types = sorted(by_type.items(), key=lambda x: x[1], reverse=True)
    return {"total_mistakes": len(mistakes), "total_occurrences": sum(by_type.values()), "by_type": [{"type": t, "count": c} for t, c in sorted_types]}