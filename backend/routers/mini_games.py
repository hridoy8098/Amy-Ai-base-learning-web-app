"""
Feature #18 — Mini Games
Word Scramble, Sentence Builder, Speed Translation, Memory Match।
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from core.ai_providers import call_ai
from models.models import User
import json, re, random

router = APIRouter()

class GameRequest(BaseModel):
    game_type: str  # scramble, sentence_builder, translation, memory
    difficulty: str = "intermediate"
    language: str = "en"

class GameSubmit(BaseModel):
    game_type: str
    answers: list
    time_seconds: int = 60

@router.get("/list")
def get_games():
    return [
        {"id": "scramble",         "name": "Word Scramble",       "icon": "🔀", "description": "Unscramble the letters to form a word", "xp": 10},
        {"id": "sentence_builder", "name": "Sentence Builder",    "icon": "🏗️", "description": "Arrange words to build a correct sentence", "xp": 15},
        {"id": "translation",      "name": "Speed Translation",   "icon": "⚡", "description": "Translate words as fast as you can", "xp": 20},
        {"id": "memory",           "name": "Memory Match",        "icon": "🃏", "description": "Match words with their definitions", "xp": 15},
    ]

@router.post("/generate")
async def generate_game(req: GameRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    lang_note = "Bangla-English" if req.language == "bn" else "English"

    prompts = {
        "scramble": f"Generate 8 {req.difficulty} {lang_note} vocabulary words for a word scramble game. Return JSON: {{\"words\":[{{\"original\":\"...\",\"scrambled\":\"...\",\"hint\":\"...\"}}]}}",
        "sentence_builder": f"Generate 5 {req.difficulty} English sentences broken into words for arrangement. Return JSON: {{\"sentences\":[{{\"words\":[\"...\"],\"correct_order\":[0,1,2],\"translation\":\"...\"}}]}}",
        "translation": f"Generate 10 {req.difficulty} {lang_note} word pairs. Return JSON: {{\"pairs\":[{{\"english\":\"...\",\"translation\":\"...\",\"example\":\"...\"}}]}}",
        "memory": f"Generate 8 {req.difficulty} English word-definition pairs. Return JSON: {{\"pairs\":[{{\"word\":\"...\",\"definition\":\"...\"}}]}}",
    }

    system = "You are a language game generator. Return ONLY valid JSON. No markdown, no backticks."
    msgs = [{"role": "user", "content": prompts.get(req.game_type, prompts["scramble"])}]

    try:
        raw, provider = await call_ai(system, msgs)
        raw = raw.strip()
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if m: data = json.loads(m.group())
        else: raise ValueError()
        return {"game_type": req.game_type, "data": data, "provider": provider}
    except Exception as e:
        # Fallback static data
        fallback = {
            "scramble": {"words": [{"original": "beautiful", "scrambled": "fuabeitul", "hint": "attractive"},{"original": "knowledge", "scrambled": "geledwonk", "hint": "information"},{"original": "practice", "scrambled": "cepratic", "hint": "to do repeatedly"}]},
            "sentence_builder": {"sentences": [{"words": ["She", "is", "reading", "a", "book"], "correct_order": [0,1,2,3,4], "translation": "সে একটা বই পড়ছে"}]},
            "translation": {"pairs": [{"english": "apple", "translation": "আপেল", "example": "I eat an apple daily."}]},
            "memory": {"pairs": [{"word": "ambiguous", "definition": "having more than one possible meaning"}]},
        }
        return {"game_type": req.game_type, "data": fallback.get(req.game_type, {})}

@router.post("/submit")
def submit_game(req: GameSubmit, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    correct = sum(1 for a in req.answers if a.get("correct", False))
    total = len(req.answers)
    score = round((correct / total * 100) if total > 0 else 0, 1)
    base_xp = {"scramble": 10, "sentence_builder": 15, "translation": 20, "memory": 15}.get(req.game_type, 10)
    time_bonus = max(0, 10 - req.time_seconds // 30)
    xp = int(base_xp * (score / 100)) + time_bonus
    user.xp_points += xp
    db.commit()
    return {"score": score, "correct": correct, "total": total, "xp_earned": xp, "time_seconds": req.time_seconds}
