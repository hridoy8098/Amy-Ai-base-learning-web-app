"""
Feature #4 — Pronunciation Checker
User word বলবে, Amy সঠিক pronunciation বলবে ও explain করবে।
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

class PronunciationRequest(BaseModel):
    word: str
    language: str = "en"

class PhraseRequest(BaseModel):
    phrase: str
    accent: str = "american"
    language: str = "en"

@router.post("/word")
async def check_pronunciation(req: PronunciationRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    lang_note = "with Bangla explanation" if req.language == "bn" else ""
    system = (
        f"You are a pronunciation expert {lang_note}. Return ONLY valid JSON:\n"
        '{"word":"...","ipa":"...","syllables":"...","stress":"...","audio_description":"...",'
        '"common_mistakes":["..."],"tips":["..."],"similar_words":["..."],"example_sentences":["..."]}'
    )
    msgs = [{"role": "user", "content": f"Explain pronunciation of: '{req.word}'"}]
    try:
        raw, provider = await call_ai(system, msgs)
        m = re.search(r'\{.*\}', raw.strip(), re.DOTALL)
        if m:
            data = json.loads(m.group())
            data["provider"] = provider
            return data
    except: pass
    return {"word": req.word, "ipa": f"/{req.word}/", "syllables": req.word, "stress": "first syllable", "audio_description": f"Pronounce '{req.word}' clearly.", "common_mistakes": [], "tips": ["Listen to native speakers"], "similar_words": [], "example_sentences": [f"Please say '{req.word}' clearly."]}

@router.post("/phrase")
async def check_phrase(req: PhraseRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    lang_note = "with Bangla explanation" if req.language == "bn" else ""
    system = (
        f"You are a {req.accent} accent pronunciation coach {lang_note}. Return ONLY valid JSON:\n"
        '{"phrase":"...","word_by_word":[{"word":"...","ipa":"...","tip":"..."}],'
        '"rhythm_pattern":"...","connected_speech_tips":["..."],"practice_steps":["..."]}'
    )
    msgs = [{"role": "user", "content": f"Explain pronunciation of phrase: '{req.phrase}' in {req.accent} English."}]
    try:
        raw, provider = await call_ai(system, msgs)
        m = re.search(r'\{.*\}', raw.strip(), re.DOTALL)
        if m:
            data = json.loads(m.group())
            data["provider"] = provider
            return data
    except: pass
    return {"phrase": req.phrase, "word_by_word": [], "rhythm_pattern": "natural", "connected_speech_tips": ["Speak slowly at first"], "practice_steps": ["Listen", "Repeat", "Record yourself"]}

@router.get("/common-mistakes")
async def common_mistakes(language: str = "en"):
    mistakes = [
        {"bangladeshi_mistake": "বাংলাদেশীরা 'v' কে 'b' বলে", "example": "'very' → 'bery'", "fix": "Upper teeth on lower lip for 'v'"},
        {"bangladeshi_mistake": "'w' কে 'v' বলে",                "example": "'water' → 'vater'", "fix": "Round lips for 'w', no teeth"},
        {"bangladeshi_mistake": "শেষের consonant drop",          "example": "'test' → 'tes'",  "fix": "Always pronounce final consonants"},
        {"bangladeshi_mistake": "th sound নেই",                  "example": "'the' → 'de'",    "fix": "Tongue between teeth for 'th'"},
        {"bangladeshi_mistake": "Silent letters উচ্চারণ",         "example": "'knife' → 'k-nife'","fix": "Learn common silent letter patterns"},
    ]
    return {"common_mistakes": mistakes}
