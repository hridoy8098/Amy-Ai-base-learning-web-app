"""
Feature #15 — Song-Based Learning
Popular song lyrics দিয়ে lesson, blank fill, pronunciation practice।
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

SONGS = [
    {"id": 1, "title": "Let Her Go",        "artist": "Passenger",      "level": "beginner",      "theme": "loss, regret"},
    {"id": 2, "title": "Shape of You",       "artist": "Ed Sheeran",     "level": "intermediate",  "theme": "romance, attraction"},
    {"id": 3, "title": "Imagine",            "artist": "John Lennon",    "level": "intermediate",  "theme": "peace, hope"},
    {"id": 4, "title": "Bohemian Rhapsody",  "artist": "Queen",          "level": "advanced",      "theme": "complex emotions"},
    {"id": 5, "title": "Someone Like You",   "artist": "Adele",          "level": "intermediate",  "theme": "heartbreak"},
]

class SongLessonRequest(BaseModel):
    song_id: int
    language: str = "en"

@router.get("/songs")
def get_songs():
    return SONGS

@router.post("/lesson")
async def song_lesson(req: SongLessonRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    song = next((s for s in SONGS if s["id"] == req.song_id), SONGS[0])
    lang_note = "with Bangla explanations" if req.language == "bn" else ""

    system = (
        f"You are a music-based English teacher {lang_note}. Create a lesson based on the song. "
        "Return ONLY valid JSON (do NOT include actual copyrighted lyrics):\n"
        '{"song_theme":"...","key_vocabulary":[{"word":"...","definition":"...","example":"..."}],'
        '"grammar_points":["..."],"fill_blanks":[{"sentence":"I only miss ___ when I close my ___","answers":["her","eyes"]}],'
        '"pronunciation_tips":["..."],"cultural_context":"...","discussion_questions":["..."]}'
    )
    msgs = [{"role": "user", "content": f"Create English lesson for song '{song['title']}' by {song['artist']}. Theme: {song['theme']}"}]

    try:
        raw, provider = await call_ai(system, msgs)
        m = re.search(r'\{.*\}', raw.strip(), re.DOTALL)
        if m: data = json.loads(m.group())
        else: raise ValueError()
        user.xp_points += 10
        db.commit()
        return {"song": song, "lesson": data, "provider": provider}
    except Exception as e:
        return {"song": song, "lesson": {"song_theme": song["theme"], "key_vocabulary": [], "grammar_points": [], "fill_blanks": [], "pronunciation_tips": [], "cultural_context": "", "discussion_questions": []}, "error": str(e)}
