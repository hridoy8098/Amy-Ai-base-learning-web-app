"""
Feature #13 — AI Learning Style Detection
৫টা interaction-এর পর visual/auditory/reading learner detect করবে।
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from core.ai_providers import call_ai
from models.models import User, AmyMessage
import json, re

router = APIRouter()

@router.get("/detect")
async def detect_style(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    msgs = db.query(AmyMessage).filter(AmyMessage.user_id == user.id, AmyMessage.role == "user").order_by(AmyMessage.created_at.desc()).limit(20).all()
    if len(msgs) < 5:
        return {"detected": False, "message": "Have at least 5 conversations with Amy to detect your learning style!", "interactions_needed": 5 - len(msgs)}

    sample = [m.content for m in msgs[:15]]
    system = (
        "You are a learning style analyst. Based on the user's messages, detect their learning style. "
        "Return ONLY valid JSON:\n"
        '{"style":"visual","confidence":85,"description":"...","tips":["...","...","..."],'
        '"recommended_modes":["..."],"icon":"👁️"}'
        "\nStyles: visual, auditory, reading, kinesthetic"
    )
    msgs_ai = [{"role": "user", "content": f"Analyze these user messages:\n{json.dumps(sample)}\nDetect learning style."}]

    try:
        raw, _ = await call_ai(system, msgs_ai)
        m = re.search(r'\{.*\}', raw.strip(), re.DOTALL)
        if m: data = json.loads(m.group())
        else: raise ValueError("No JSON")
    except:
        data = {"style": "reading", "confidence": 70, "description": "You prefer reading and writing to learn.", "tips": ["Read articles daily", "Keep a vocabulary journal", "Write summaries"], "recommended_modes": ["english", "general"], "icon": "📖"}

    return {"detected": True, "learning_style": data, "total_interactions": len(msgs)}

@router.get("/styles")
def get_all_styles():
    return [
        {"style": "visual",      "icon": "👁️",  "description": "Learn best with images, diagrams, videos"},
        {"style": "auditory",    "icon": "👂", "description": "Learn best by listening and speaking"},
        {"style": "reading",     "icon": "📖", "description": "Learn best through reading and writing"},
        {"style": "kinesthetic", "icon": "🤸", "description": "Learn best through practice and doing"},
    ]
