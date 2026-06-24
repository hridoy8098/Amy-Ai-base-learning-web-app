"""
Feature #5 — AI Essay Checker
Grammar, vocabulary, coherence check করে।
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

class EssayRequest(BaseModel):
    text: str
    language: str = "en"

@router.post("/check")
async def check_essay(req: EssayRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if len(req.text.strip()) < 20:
        return {"error": "Text too short. Write at least 20 characters."}

    system = (
        "You are an expert English writing coach. Analyze the essay/paragraph and return ONLY valid JSON:\n"
        '{"overall_score":85,"grammar_score":80,"vocabulary_score":85,"coherence_score":90,'
        '"grammar_errors":[{"original":"...","correction":"...","explanation":"..."}],'
        '"vocabulary_suggestions":[{"word":"...","better_alternatives":["..."],"reason":"..."}],'
        '"coherence_feedback":"...","strengths":["..."],"improvements":["..."],"corrected_text":"..."}'
    )
    msgs = [{"role": "user", "content": f"Check this text:\n\n{req.text}"}]

    try:
        raw, provider = await call_ai(system, msgs)
        raw = raw.strip()
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if m: raw = m.group()
        data = json.loads(raw)
        data["provider"] = provider
        user.xp_points += 5
        db.commit()
        return data
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}", "overall_score": 0}
