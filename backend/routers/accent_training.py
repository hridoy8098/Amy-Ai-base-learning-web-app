"""
Feature #30 — Accent Training
British/American/Australian accent practice with AI feedback।
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from core.ai_providers import call_ai
from models.models import User
import json, re

router = APIRouter()

ACCENTS = [
    {"id": "american", "name": "American English",   "icon": "🇺🇸", "description": "General American accent — most widely used in media"},
    {"id": "british",  "name": "British English",    "icon": "🇬🇧", "description": "Received Pronunciation (RP) — BBC English style"},
    {"id": "australian","name": "Australian English","icon": "🇦🇺", "description": "Australian accent — relaxed and friendly"},
    {"id": "neutral",  "name": "Neutral English",    "icon": "🌍", "description": "Clear, accent-neutral English for international communication"},
]

PRACTICE_WORDS = {
    "american":  [("water", "WAH-ter"), ("butter", "BUH-ter"), ("can't", "kant"), ("schedule", "SKED-yool")],
    "british":   [("water", "WAW-ter"), ("butter", "BUH-tuh"), ("can't", "kahnt"), ("schedule", "SHED-yool")],
    "australian":[("water", "WAW-tah"), ("mate", "mayt"), ("no worries", "noh WOR-eez"), ("arvo", "AH-voh")],
    "neutral":   [("hello", "heh-LOH"), ("important", "im-POR-tent"), ("presentation", "prez-en-TAY-shun")],
}

class AccentPracticeRequest(BaseModel):
    accent_id: str
    text: Optional[str] = None
    language: str = "en"

@router.get("/accents")
def get_accents():
    return ACCENTS

@router.post("/lesson")
async def accent_lesson(req: AccentPracticeRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    accent = next((a for a in ACCENTS if a["id"] == req.accent_id), ACCENTS[0])
    practice_words = PRACTICE_WORDS.get(req.accent_id, PRACTICE_WORDS["neutral"])
    lang_note = "with Bangla explanations" if req.language == "bn" else ""

    system = (
        f"You are an accent coach teaching {accent['name']} {lang_note}. "
        "Return ONLY valid JSON:\n"
        '{"key_features":["..."],"vowel_sounds":[{"sound":"...","example_word":"...","tip":"..."}],'
        '"common_differences":["..."],"practice_sentences":["..."],'
        '"tongue_twisters":["..."],"tips":["..."]}'
    )
    msgs = [{"role": "user", "content": f"Create {accent['name']} accent lesson. " + (f"Practice text: {req.text}" if req.text else "General introduction.")}]

    try:
        raw, provider = await call_ai(system, msgs)
        m = re.search(r'\{.*\}', raw.strip(), re.DOTALL)
        if m: data = json.loads(m.group())
        else: raise ValueError()
        user.xp_points += 10
        db.commit()
        return {"accent": accent, "lesson": data, "practice_words": [{"word": w[0], "pronunciation": w[1]} for w in practice_words], "provider": provider}
    except:
        return {"accent": accent, "lesson": {"key_features": [f"Learn key features of {accent['name']}"], "vowel_sounds": [], "common_differences": [], "practice_sentences": ["How are you today?", "Could you please repeat that?"], "tongue_twisters": ["She sells seashells by the seashore"], "tips": ["Listen to native speakers", "Record yourself and compare"]}, "practice_words": [{"word": w[0], "pronunciation": w[1]} for w in practice_words]}

@router.get("/minimal-pairs")
async def minimal_pairs(accent_id: str = "american"):
    pairs = [
        {"word1": "ship", "word2": "sheep", "tip": "Short 'i' vs long 'ee'"},
        {"word1": "bit",  "word2": "beat",  "tip": "Short 'i' vs long 'ee'"},
        {"word1": "full", "word2": "fool",  "tip": "Short 'oo' vs long 'oo'"},
        {"word1": "hat",  "word2": "hot",   "tip": "Short 'a' vs short 'o'"},
        {"word1": "live", "word2": "leave", "tip": "Short 'i' vs long 'ee'"},
    ]
    return {"accent_id": accent_id, "minimal_pairs": pairs}
