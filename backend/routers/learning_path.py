"""
Feature #1 — AI Personalized Learning Path
Quiz results + weak points দেখে AI next lesson/course suggest করে।
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from core.ai_providers import call_ai
from models.models import User, QuizResult, Enrollment, Course
import json, re

router = APIRouter()

@router.get("/")
async def get_learning_path(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    results = db.query(QuizResult).filter(QuizResult.user_id == user.id).order_by(QuizResult.created_at.desc()).limit(10).all()
    weak = [{"topic": r.topic, "score": r.score} for r in results if r.score < 60]
    good = [{"topic": r.topic, "score": r.score} for r in results if r.score >= 60]

    done_ids = {e.course_id for e in db.query(Enrollment).filter(Enrollment.user_id == user.id, Enrollment.completed == True).all()}
    available = db.query(Course).filter(Course.status == "published").order_by(Course.enrolled_count.desc()).limit(20).all()
    av_list = [{"id": c.id, "title": c.title, "level": c.level, "tags": c.tags or []} for c in available if c.id not in done_ids]

    system = (
        "You are a learning path advisor. Based on the user's quiz performance, "
        "recommend a personalized learning path. Return ONLY valid JSON:\n"
        '{"summary":"...","weak_areas":["..."],"recommended_courses":[{"id":1,"reason":"..."}],'
        '"next_steps":["..."],"encouragement":"..."}'
    )
    msgs = [{"role": "user", "content":
        f"User: level={user.level}, xp={user.xp_points}\n"
        f"Weak topics (score<60): {json.dumps(weak)}\n"
        f"Strong topics: {json.dumps(good)}\n"
        f"Available courses: {json.dumps(av_list[:10])}\n"
        "Give personalized learning path."}]

    try:
        raw, provider = await call_ai(system, msgs)
        raw = raw.strip()
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if m: raw = m.group()
        data = json.loads(raw)
    except:
        data = {
            "summary": "Keep practicing daily to improve your English!",
            "weak_areas": [w["topic"] for w in weak[:3]],
            "recommended_courses": [{"id": c["id"], "reason": "Good match for your level"} for c in av_list[:3]],
            "next_steps": ["Practice speaking daily", "Review grammar basics", "Take more quizzes"],
            "encouragement": "You're doing great! Keep it up!"
        }

    rec_courses = []
    for rc in data.get("recommended_courses", [])[:5]:
        c = db.query(Course).filter(Course.id == rc.get("id")).first()
        if c:
            rec_courses.append({"id": c.id, "title": c.title, "slug": c.slug, "level": c.level, "thumbnail": c.thumbnail, "reason": rc.get("reason", "")})

    return {"path": data, "recommended_courses": rec_courses, "weak_topics": weak, "provider": provider if 'provider' in dir() else ""}
