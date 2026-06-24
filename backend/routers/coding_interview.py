"""
Feature #29 — Coding Interview Practice
IT professionals-দের English-এ technical concepts explain করা।
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

TECH_TOPICS = [
    {"id": "oop",        "name": "Object-Oriented Programming",  "icon": "🏗️"},
    {"id": "algorithms", "name": "Data Structures & Algorithms",  "icon": "🔢"},
    {"id": "system",     "name": "System Design",                 "icon": "🖥️"},
    {"id": "databases",  "name": "Databases & SQL",               "icon": "🗄️"},
    {"id": "api",        "name": "APIs & Web Services",           "icon": "🔌"},
    {"id": "cloud",      "name": "Cloud Computing",               "icon": "☁️"},
    {"id": "agile",      "name": "Agile & Scrum",                 "icon": "🔄"},
    {"id": "behavioral", "name": "Behavioral Questions",          "icon": "🤝"},
]

class InterviewRequest(BaseModel):
    topic_id: str
    difficulty: str = "intermediate"
    language: str = "en"
    num_questions: int = 5

class InterviewSubmit(BaseModel):
    question: str
    answer: str
    topic_id: str

@router.get("/topics")
def get_topics():
    return TECH_TOPICS

@router.post("/questions")
async def get_interview_questions(req: InterviewRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    topic = next((t for t in TECH_TOPICS if t["id"] == req.topic_id), TECH_TOPICS[0])
    lang_note = "with Bangla explanations" if req.language == "bn" else ""

    system = (
        f"You are a senior software engineer conducting a technical interview {lang_note}. "
        "Return ONLY valid JSON:\n"
        '{"questions":[{"id":1,"question":"...","type":"technical","difficulty":"intermediate",'
        '"hints":["..."],"what_interviewer_looks_for":"..."}]}'
    )
    msgs = [{"role": "user", "content": f"Generate {req.num_questions} {req.difficulty} interview questions about {topic['name']}."}]

    try:
        raw, provider = await call_ai(system, msgs)
        m = re.search(r'\{.*\}', raw.strip(), re.DOTALL)
        if m: data = json.loads(m.group())
        else: raise ValueError()
        return {"topic": topic, "questions": data.get("questions", []), "provider": provider}
    except:
        return {"topic": topic, "questions": [{"id": 1, "question": f"Explain {topic['name']} in simple English.", "type": "technical", "difficulty": req.difficulty, "hints": ["Start with a definition", "Give an example"], "what_interviewer_looks_for": "Clear communication and technical knowledge"}]}

@router.post("/evaluate")
async def evaluate_answer(req: InterviewSubmit, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    system = (
        "You are a senior interviewer evaluating a candidate's English response. "
        "Return ONLY valid JSON:\n"
        '{"score":75,"english_clarity":80,"technical_accuracy":70,'
        '"grammar_issues":["..."],"vocabulary_suggestions":["..."],'
        '"better_answer":"...","feedback":"...","xp_earned":15}'
    )
    msgs = [{"role": "user", "content": f"Question: {req.question}\n\nCandidate's answer: {req.answer}\n\nEvaluate the English and technical accuracy."}]

    try:
        raw, provider = await call_ai(system, msgs)
        m = re.search(r'\{.*\}', raw.strip(), re.DOTALL)
        if m:
            data = json.loads(m.group())
            xp = data.get("xp_earned", 15)
            user.xp_points += xp
            db.commit()
            data["provider"] = provider
            return data
    except:
        pass
    return {"score": 70, "english_clarity": 70, "technical_accuracy": 70, "grammar_issues": [], "vocabulary_suggestions": [], "better_answer": "Practice explaining this concept more clearly.", "feedback": "Good attempt! Keep practicing.", "xp_earned": 10}
