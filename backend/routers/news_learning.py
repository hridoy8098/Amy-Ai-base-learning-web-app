"""
Feature #14 — News-Based Learning
BBC/CNN headlines থেকে lesson — English + world news একসাথে।
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

SAMPLE_TOPICS = [
    {"id": 1, "category": "Technology", "headline": "AI Revolution Changes How We Work and Learn", "source": "Tech News"},
    {"id": 2, "category": "Environment", "headline": "Scientists Discover New Ways to Combat Climate Change", "source": "Science Daily"},
    {"id": 3, "category": "Health",      "headline": "New Study Shows Benefits of Daily Exercise on Mental Health", "source": "Health Weekly"},
    {"id": 4, "category": "Business",    "headline": "Global Economy Shows Signs of Recovery After Challenges", "source": "Business Times"},
    {"id": 5, "category": "Education",   "headline": "Online Learning Platforms See Record Growth Worldwide", "source": "Edu News"},
]

class NewsLessonRequest(BaseModel):
    topic_id: int
    difficulty: str = "intermediate"
    language: str = "en"

@router.get("/topics")
def get_topics():
    return SAMPLE_TOPICS

@router.post("/lesson")
async def generate_news_lesson(req: NewsLessonRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    topic = next((t for t in SAMPLE_TOPICS if t["id"] == req.topic_id), SAMPLE_TOPICS[0])
    lang_note = "in Bangla with English vocabulary highlighted" if req.language == "bn" else "in English"

    system = (
        f"You are an English teacher creating a news-based lesson {lang_note}. "
        "Return ONLY valid JSON:\n"
        '{"title":"...","summary":"...","key_vocabulary":[{"word":"...","definition":"...","example":"..."}],'
        '"comprehension_questions":["...","...","..."],"discussion_points":["...","..."],'
        '"grammar_focus":"...","cultural_note":"..."}'
    )
    msgs = [{"role": "user", "content": f"Create a {req.difficulty} lesson from this headline: '{topic['headline']}'"}]

    try:
        raw, provider = await call_ai(system, msgs)
        m = re.search(r'\{.*\}', raw.strip(), re.DOTALL)
        if m: data = json.loads(m.group())
        else: raise ValueError()
        user.xp_points += 10
        db.commit()
        return {"topic": topic, "lesson": data, "provider": provider}
    except Exception as e:
        return {"topic": topic, "lesson": {"title": topic["headline"], "summary": "Read and learn from today's news.", "key_vocabulary": [], "comprehension_questions": [], "discussion_points": [], "grammar_focus": "", "cultural_note": ""}, "error": str(e)}
