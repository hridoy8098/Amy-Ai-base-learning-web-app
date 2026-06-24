"""
Feature #16 — Sleep Learning Mode
ঘুমানোর আগে ৫ মিনিটের recap — scientifically proven effective।
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from core.ai_providers import call_ai
from models.models import User, AmyMessage, SavedVocab, QuizResult
import json, re

router = APIRouter()

@router.get("/recap")
async def get_sleep_recap(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Collect today's learning
    recent_msgs = db.query(AmyMessage).filter(AmyMessage.user_id == user.id, AmyMessage.role == "user").order_by(AmyMessage.created_at.desc()).limit(10).all()
    recent_vocab = db.query(SavedVocab).filter(SavedVocab.user_id == user.id).order_by(SavedVocab.created_at.desc()).limit(5).all()
    recent_quiz = db.query(QuizResult).filter(QuizResult.user_id == user.id).order_by(QuizResult.created_at.desc()).limit(3).all()

    vocab_list = [{"word": v.word, "definition": v.definition} for v in recent_vocab]
    quiz_topics = [{"topic": q.topic, "score": q.score} for q in recent_quiz]

    system = (
        "You are a sleep learning coach. Create a gentle 5-minute bedtime recap to reinforce today's learning. "
        "Be calm, soothing, and encouraging. Return ONLY valid JSON:\n"
        '{"title":"Tonight\'s Learning Recap","greeting":"...","todays_highlights":["..."],'
        '"vocab_review":[{"word":"...","simple_definition":"...","memory_tip":"..."}],'
        '"key_takeaway":"...","tomorrow_preview":"...","bedtime_affirmation":"...", "duration_minutes":5}'
    )
    msgs = [{"role": "user", "content":
        f"Create bedtime recap for: vocab learned={json.dumps(vocab_list)}, quiz topics={json.dumps(quiz_topics)}, "
        f"user level={user.level}, streak={user.streak_days} days"}]

    try:
        raw, provider = await call_ai(system, msgs)
        m = re.search(r'\{.*\}', raw.strip(), re.DOTALL)
        if m: data = json.loads(m.group())
        else: raise ValueError()
        return {"recap": data, "provider": provider}
    except:
        return {"recap": {
            "title": "Tonight's Learning Recap",
            "greeting": f"Great work today, {user.name}! 🌙",
            "todays_highlights": ["You practiced English today", f"You're on a {user.streak_days}-day streak!"],
            "vocab_review": vocab_list[:3],
            "key_takeaway": "Consistency is the key to fluency. You're doing great!",
            "tomorrow_preview": "Tomorrow, try a new roleplay scenario with Amy.",
            "bedtime_affirmation": "You are becoming more fluent every day. Sweet dreams! 💤",
            "duration_minutes": 5
        }}
