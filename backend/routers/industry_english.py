"""
Feature #22 — Industry-Specific English
Medical, Legal, IT, Business, Travel — specialized content।
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

INDUSTRIES = [
    {"id": "medical",    "icon": "🏥", "name": "Medical English",    "description": "Doctor visits, symptoms, prescriptions, hospital vocabulary"},
    {"id": "legal",      "icon": "⚖️",  "name": "Legal English",      "description": "Contracts, rights, court, legal terminology"},
    {"id": "it",         "icon": "💻", "name": "IT/Tech English",     "description": "Programming, software, tech meetings, documentation"},
    {"id": "business",   "icon": "💼", "name": "Business English",    "description": "Meetings, presentations, emails, negotiation"},
    {"id": "travel",     "icon": "✈️",  "name": "Travel English",      "description": "Airport, hotel, directions, booking, tourism"},
    {"id": "academic",   "icon": "🎓", "name": "Academic English",    "description": "Essays, research, presentations, IELTS/TOEFL prep"},
    {"id": "hospitality","icon": "🍽️", "name": "Hospitality English", "description": "Restaurant, hotel service, customer care"},
    {"id": "finance",    "icon": "💰", "name": "Finance English",     "description": "Banking, investment, accounting terminology"},
]

class IndustryLessonRequest(BaseModel):
    industry_id: str
    topic: str = "general"
    difficulty: str = "intermediate"
    language: str = "en"

@router.get("/industries")
def get_industries():
    return INDUSTRIES

@router.post("/lesson")
async def industry_lesson(req: IndustryLessonRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    industry = next((i for i in INDUSTRIES if i["id"] == req.industry_id), INDUSTRIES[3])
    lang_note = "with Bangla translations" if req.language == "bn" else ""

    system = (
        f"You are an expert {industry['name']} teacher {lang_note}. "
        "Create a practical lesson. Return ONLY valid JSON:\n"
        '{"title":"...","introduction":"...","key_terms":[{"term":"...","definition":"...","example_sentence":"..."}],'
        '"common_phrases":[{"phrase":"...","usage":"...","context":"..."}],'
        '"sample_dialogue":[{"speaker":"...","line":"..."}],'
        '"practice_exercise":{"instructions":"...","scenario":"...","hints":["..."]},'
        '"pro_tips":["..."]}'
    )
    msgs = [{"role": "user", "content": f"Create {req.difficulty} lesson for {industry['name']}. Topic: {req.topic}"}]

    try:
        raw, provider = await call_ai(system, msgs)
        m = re.search(r'\{.*\}', raw.strip(), re.DOTALL)
        if m: data = json.loads(m.group())
        else: raise ValueError()
        user.xp_points += 15
        db.commit()
        return {"industry": industry, "lesson": data, "provider": provider}
    except Exception as e:
        return {"industry": industry, "lesson": {"title": f"{industry['name']} Basics", "introduction": "Let's learn industry-specific English!", "key_terms": [], "common_phrases": [], "sample_dialogue": [], "practice_exercise": {"instructions": "Practice using these terms", "scenario": "", "hints": []}, "pro_tips": []}, "error": str(e)}

@router.get("/{industry_id}/topics")
def get_industry_topics(industry_id: str):
    topics = {
        "medical":  ["Patient Consultation", "Medical History", "Emergency Room", "Pharmacy", "Surgery"],
        "legal":    ["Contract Review", "Court Proceedings", "Legal Advice", "Rights & Obligations", "Settlements"],
        "it":       ["Code Review", "Bug Report", "Sprint Planning", "System Architecture", "API Documentation"],
        "business": ["Board Meeting", "Sales Pitch", "Performance Review", "Email Writing", "Negotiation"],
        "travel":   ["Check-in", "Customs", "Asking Directions", "Hotel Booking", "Emergency Situations"],
        "academic": ["Essay Writing", "Research Presentation", "IELTS Speaking", "Academic Vocabulary", "Thesis Defense"],
        "hospitality": ["Table Service", "Complaints Handling", "Reservations", "Room Service", "Check-out"],
        "finance":  ["Investment Analysis", "Budget Meeting", "Banking Terms", "Financial Reports", "Tax Discussion"],
    }
    return {"industry_id": industry_id, "topics": topics.get(industry_id, ["General"])}
