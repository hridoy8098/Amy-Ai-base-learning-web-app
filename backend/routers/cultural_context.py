"""
Feature #21 — Cultural Context Learning
Grammar-এর পাশে English-speaking culture শেখাবে।
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from core.ai_providers import call_ai
from models.models import User
import json, re

router = APIRouter()

CULTURAL_TOPICS = [
    {"id": "small_talk",   "icon": "💬", "name": "Small Talk",         "description": "Weather, weekend, sports — what English speakers chat about"},
    {"id": "politeness",   "icon": "🤝", "name": "Politeness & Manners","description": "Please, thank you, social norms in English culture"},
    {"id": "humor",        "icon": "😄", "name": "English Humor",       "description": "Sarcasm, irony, British vs American jokes"},
    {"id": "idioms",       "icon": "🗣️", "name": "Idioms in Context",   "description": "Why English speakers say 'break a leg' — not literally!"},
    {"id": "workplace",    "icon": "🏢", "name": "Workplace Culture",   "description": "Emails, meetings, how to be professional"},
    {"id": "holidays",     "icon": "🎄", "name": "Holidays & Traditions","description": "Christmas, Thanksgiving, Halloween — vocabulary and customs"},
    {"id": "media",        "icon": "📺", "name": "Pop Culture & Media",  "description": "Movies, music, TV references English speakers use"},
    {"id": "food_culture", "icon": "🍔", "name": "Food & Dining Culture","description": "Tipping, table manners, food vocabulary"},
]

class CulturalRequest(BaseModel):
    topic_id: str
    language: str = "en"

@router.get("/topics")
def get_topics():
    return CULTURAL_TOPICS

@router.post("/lesson")
async def cultural_lesson(req: CulturalRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    topic = next((t for t in CULTURAL_TOPICS if t["id"] == req.topic_id), CULTURAL_TOPICS[0])
    lang_note = "with Bangla explanations and comparisons to Bangladeshi culture" if req.language == "bn" else ""

    system = (
        f"You are a cultural English teacher {lang_note}. Teach about {topic['name']}. "
        "Return ONLY valid JSON:\n"
        '{"title":"...","introduction":"...","key_concepts":[{"concept":"...","explanation":"...","example":"..."}],'
        '"dos":["..."],"donts":["..."],"sample_conversations":[{"context":"...","dialogue":[{"speaker":"A","line":"..."}]}],'
        '"cultural_notes":["..."],"fun_facts":["..."]}'
    )
    msgs = [{"role": "user", "content": f"Teach me about {topic['name']} in English-speaking cultures."}]

    try:
        raw, provider = await call_ai(system, msgs)
        m = re.search(r'\{.*\}', raw.strip(), re.DOTALL)
        if m:
            data = json.loads(m.group())
            user.xp_points += 10
            db.commit()
            return {"topic": topic, "lesson": data, "provider": provider}
    except: pass
    return {"topic": topic, "lesson": {"title": topic["name"], "introduction": f"Let's learn about {topic['name']}!", "key_concepts": [], "dos": [], "donts": [], "sample_conversations": [], "cultural_notes": [], "fun_facts": []}}
