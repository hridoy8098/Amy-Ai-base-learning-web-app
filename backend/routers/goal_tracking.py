"""
Feature #28 — Goal Setting and Tracking
IELTS/TOEFL goal set করলে Amy study plan তৈরি করবে।
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from core.ai_providers import call_ai
from models.models import User, UserGoal
import json, re
from datetime import datetime

router = APIRouter()

class GoalCreate(BaseModel):
    goal_type: str
    target_score: Optional[float] = None
    deadline: Optional[str] = None
    current_level: str = "intermediate"

GOAL_TYPES = [
    {"id": "ielts",    "icon": "🎓", "name": "IELTS Preparation",   "description": "Target band 6.0 - 8.0"},
    {"id": "toefl",    "icon": "📝", "name": "TOEFL Preparation",   "description": "Target score 80 - 120"},
    {"id": "business", "icon": "💼", "name": "Business English",    "description": "Professional communication"},
    {"id": "travel",   "icon": "✈️",  "name": "Travel English",      "description": "Confident traveling"},
    {"id": "general",  "icon": "📚", "name": "General Fluency",     "description": "Everyday English improvement"},
    {"id": "interview","icon": "🤝", "name": "Job Interview",       "description": "Get your dream job"},
]

@router.get("/types")
def get_goal_types():
    return GOAL_TYPES

@router.get("/")
def get_goals(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    goals = db.query(UserGoal).filter(UserGoal.user_id == user.id, UserGoal.is_active == True).all()
    result = []
    for g in goals:
        plan = json.loads(g.study_plan) if g.study_plan else {}
        result.append({"id": g.id, "goal_type": g.goal_type, "target_score": g.target_score, "deadline": g.deadline.isoformat() if g.deadline else None, "study_plan": plan, "progress_pct": g.progress_pct, "created_at": g.created_at.isoformat()})
    return result

@router.post("/create")
async def create_goal(req: GoalCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    goal_info = next((g for g in GOAL_TYPES if g["id"] == req.goal_type), GOAL_TYPES[-1])
    deadline_str = req.deadline or "3 months"

    system = (
        "You are an English learning coach. Create a detailed study plan. Return ONLY valid JSON:\n"
        '{"weekly_plan":[{"week":1,"focus":"...","activities":["..."],"hours":5}],'
        '"daily_tasks":["..."],"key_milestones":["..."],"resources":["..."],'
        '"tips":["..."],"estimated_weeks":12}'
    )
    msgs = [{"role": "user", "content":
        f"Create study plan for {goal_info['name']}. "
        f"Target score: {req.target_score or 'N/A'}. Deadline: {deadline_str}. "
        f"Current level: {req.current_level}. User XP level: {user.level}"}]

    try:
        raw, _ = await call_ai(system, msgs)
        m = re.search(r'\{.*\}', raw.strip(), re.DOTALL)
        plan = json.loads(m.group()) if m else {}
    except:
        plan = {"weekly_plan": [{"week": 1, "focus": "Foundation", "activities": ["Study vocabulary", "Practice with Amy"], "hours": 5}], "daily_tasks": ["30 min Amy conversation", "10 new words", "1 quiz"], "key_milestones": ["Complete beginner course", "Score 70% on practice test"], "resources": ["Amy AI Tutor", "Vocabulary flashcards"], "tips": ["Practice daily", "Focus on weak areas"], "estimated_weeks": 12}

    deadline_dt = None
    if req.deadline:
        try: deadline_dt = datetime.fromisoformat(req.deadline)
        except: pass

    goal = UserGoal(user_id=user.id, goal_type=req.goal_type, target_score=req.target_score, deadline=deadline_dt, study_plan=json.dumps(plan))
    db.add(goal); db.commit(); db.refresh(goal)
    return {"id": goal.id, "goal_type": goal.goal_type, "study_plan": plan, "message": "Goal created with personalized study plan!"}

@router.put("/{goal_id}/progress")
def update_progress(goal_id: int, progress: float, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    goal = db.query(UserGoal).filter(UserGoal.id == goal_id, UserGoal.user_id == user.id).first()
    if not goal: raise HTTPException(404, "Goal not found")
    goal.progress_pct = min(100.0, progress)
    db.commit()
    return {"message": "Progress updated", "progress": goal.progress_pct}