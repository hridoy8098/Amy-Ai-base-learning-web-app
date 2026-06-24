"""
Amy AI Router
=============
Uses centralized ai_providers.py — Groq (10 keys rotating) → HuggingChat fallback.
No Ollama / DeepSeek / Gemini / OpenAI in this file.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from core.security import get_current_user
from core.database import get_db
from core.config import AMY_FREE_DAILY_LIMIT, AMY_FREE_VOICE_LIMIT
from core.ai_providers import call_ai, get_provider_status
from models.models import User, AmySession, AmyMessage, SavedVocab
from datetime import datetime, date

router = APIRouter()

# ── Schemas ───────────────────────────────────────────────────────

class MessageSchema(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[MessageSchema] = []
    mode: str = "general"
    scenario: Optional[str] = None
    difficulty: str = "intermediate"
    language: str = "auto"
    session_id: Optional[int] = None

class ChatResponse(BaseModel):
    reply: str
    detected_emotion: Optional[str] = None
    grammar_note: Optional[str] = None
    new_vocab: Optional[str] = None
    fluency_score: Optional[int] = None
    xp_earned: int = 5
    mood: str = "happy"
    provider: str = ""
    session_id: Optional[int] = None

class VoiceRequest(BaseModel):
    transcript: str
    history: List[MessageSchema] = []
    mode: str = "general"
    scenario: Optional[str] = None
    difficulty: str = "intermediate"
    language: str = "auto"
    session_id: Optional[int] = None

class VoiceResponse(BaseModel):
    reply: str
    detected_emotion: Optional[str] = None
    mood: str = "happy"
    provider: str = ""
    xp_earned: int = 8
    session_id: Optional[int] = None

class SaveVocabRequest(BaseModel):
    word: str
    definition: Optional[str] = None
    example: Optional[str] = None

# ── Usage limit ───────────────────────────────────────────────────

def check_and_update_usage(user: User, db: Session, is_voice: bool = False):
    today = date.today()
    last_reset = user.last_usage_reset.date() if user.last_usage_reset else None

    if last_reset != today:
        user.amy_messages_today   = 0
        user.amy_voice_today      = 0
        user.quiz_generated_today = 0
        user.last_usage_reset     = datetime.utcnow()

    is_paid = user.subscription_plan in ("basic", "pro", "premium")

    if is_voice:
        if not is_paid and user.amy_voice_today >= AMY_FREE_VOICE_LIMIT:
            raise HTTPException(402, f"Free voice limit ({AMY_FREE_VOICE_LIMIT}/day) reached. Upgrade to Pro!")
        user.amy_voice_today += 1
    else:
        if not is_paid and user.amy_messages_today >= AMY_FREE_DAILY_LIMIT:
            raise HTTPException(402, f"Free message limit ({AMY_FREE_DAILY_LIMIT}/day) reached. Upgrade to Pro!")
        user.amy_messages_today += 1

    db.commit()

# ── Helpers ───────────────────────────────────────────────────────

def detect_emotion(text: str) -> dict:
    t = text.lower()
    if any(w in t for w in ["don't understand","confused","hard","difficult",
                              "i don't get","not clear","বুঝতে পারছি না","কঠিন"]):
        return {"emotion":"confused",   "emoji":"😕","label":"Confused"}
    if any(w in t for w in ["frustrated","annoying","hate","wrong","ugh","বিরক্ত","রাগ"]):
        return {"emotion":"frustrated", "emoji":"😤","label":"Frustrated"}
    if any(w in t for w in ["boring","bored","whatever","বোরিং"]):
        return {"emotion":"bored",      "emoji":"😴","label":"Bored"}
    if any(w in t for w in ["nervous","scared","worried","shy","ভয়","লজ্জা"]):
        return {"emotion":"nervous",    "emoji":"😰","label":"Nervous"}
    if any(w in t for w in ["great","awesome","i got it","easy","love","বুঝেছি","দারুণ"]):
        return {"emotion":"confident",  "emoji":"😊","label":"Confident"}
    return {"emotion":"neutral","emoji":"🙂","label":"Neutral"}


def build_user_context(user: User) -> str:
    return (
        f"\nUser Profile: Name={user.name}, Level={user.level}, "
        f"XP={user.xp_points}, Streak={user.streak_days} days, "
        f"Subscription={user.subscription_plan}"
    )


def build_system(mode: str, scenario: Optional[str], difficulty: str,
                 emotion: str, language: str, user_ctx: str) -> str:

    base = (
        "You are Amy, a warm, encouraging, expert English tutor AI.\n"
        "Personality: friendly, funny when appropriate, patient, never judgmental.\n"
        "Respond naturally and conversationally. Keep responses concise (2-4 sentences) "
        "unless teaching something complex.\n"
        "Never reveal you are Llama, HuggingChat, Groq, or any AI model. You are ONLY Amy.\n"
        + user_ctx
    )

    if language in ("Bangla", "bn-BD"):
        lang = "\nLANGUAGE: Reply in Bangla (বাংলা). Include English examples when teaching."
    elif language == "auto":
        lang = "\nLANGUAGE: Detect user's language and reply in the SAME language."
    else:
        lang = f"\nLANGUAGE: Reply in {language}."

    emotion_hints = {
        "confused":   "\nUser is CONFUSED. Simplify. Use analogies. Break into steps.",
        "frustrated": "\nUser is FRUSTRATED. Be warm and encouraging. Simplify immediately.",
        "bored":      "\nUser is BORED. Make it fun! Add a joke or interesting fact.",
        "nervous":    "\nUser is NERVOUS. Be gentle. Remove pressure. Celebrate small wins.",
        "confident":  "\nUser is CONFIDENT. Increase difficulty. Introduce new vocabulary.",
        "neutral":    "",
    }

    mode_hints = {
        "general":  "\nMode: General English help.",
        "english":  (
            f"\nMode: English Practice ({difficulty} level).\n"
            "- Correct grammar gently after reply: [GRAMMAR: correction]\n"
            "- Teach new useful words: [VOCAB: word - definition]\n"
            "- Add fluency estimate: [FLUENCY: 0-100]\n"
            "- Ask follow-up questions to keep practice going"
        ),
        "roleplay": (
            f"\nMode: Role-Play — {scenario or 'General Conversation'}.\n"
            "Stay IN CHARACTER. Note mistakes AFTER the exchange."
        ),
        "voice": (
            "\nMode: Voice Conversation.\n"
            "Keep every reply SHORT — max 1-2 sentences. "
            "Natural spoken language only. No bullet points."
        ),
    }

    return base + lang + emotion_hints.get(emotion, "") + mode_hints.get(mode, mode_hints["general"])


def parse_response(text: str) -> dict:
    grammar_note = new_vocab = fluency_score = None
    clean = text

    for tag, key in [("[GRAMMAR:", "grammar"), ("[VOCAB:", "vocab"), ("[FLUENCY:", "fluency")]:
        if tag in clean:
            try:
                s = clean.index(tag) + len(tag)
                e = clean.index("]", s)
                val = clean[s:e].strip()
                clean = clean.replace(clean[clean.index(tag):e+1], "").strip()
                if key == "grammar":  grammar_note  = val
                elif key == "vocab":  new_vocab     = val
                elif key == "fluency":
                    try: fluency_score = int(val)
                    except: pass
            except Exception:
                pass

    return {
        "reply":         clean.strip(),
        "grammar_note":  grammar_note,
        "new_vocab":     new_vocab,
        "fluency_score": fluency_score,
    }


def get_mood(emotion: str) -> str:
    return {
        "confused":   "thinking",
        "frustrated": "caring",
        "bored":      "playful",
        "nervous":    "gentle",
        "confident":  "excited",
    }.get(emotion, "happy")


def get_or_create_session(
    user_id: int, session_id: Optional[int],
    mode: str, language: str, db: Session
) -> AmySession:
    if session_id:
        s = db.query(AmySession).filter(
            AmySession.id == session_id, AmySession.user_id == user_id
        ).first()
        if s: return s

    s = AmySession(user_id=user_id, mode=mode, language=language)
    db.add(s); db.commit(); db.refresh(s)
    return s

# ── Routes ────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        check_and_update_usage(user, db, is_voice=False)

        emotion_data = detect_emotion(req.message)
        emotion      = emotion_data["emotion"]
        user_ctx     = build_user_context(user)
        system       = build_system(
            req.mode, req.scenario, req.difficulty,
            emotion, req.language, user_ctx
        )

        messages = [{"role": m.role, "content": m.content} for m in req.history[-10:]]
        messages.append({"role": "user", "content": req.message})

        raw, provider_used = await call_ai(system, messages)
        parsed = parse_response(raw)

        xp = 5
        if req.mode == "english":  xp = 10
        if req.mode == "roleplay": xp = 15
        if parsed["fluency_score"] and parsed["fluency_score"] > 80: xp += 5

        user.xp_points += xp
        db.commit()

        session = get_or_create_session(user.id, req.session_id, req.mode, req.language, db)
        db.add(AmyMessage(session_id=session.id, user_id=user.id, role="user",  content=req.message))
        db.add(AmyMessage(session_id=session.id, user_id=user.id, role="assistant",
                          content=parsed["reply"], mood=get_mood(emotion),
                          provider=provider_used, xp_earned=xp))
        db.commit()

        return ChatResponse(
            reply            = parsed["reply"],
            detected_emotion = f"{emotion_data['emoji']} {emotion_data['label']}",
            grammar_note     = parsed["grammar_note"],
            new_vocab        = parsed["new_vocab"],
            fluency_score    = parsed["fluency_score"],
            xp_earned        = xp,
            mood             = get_mood(emotion),
            provider         = provider_used,
            session_id       = session.id,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Amy error: {str(e)}")


@router.post("/voice", response_model=VoiceResponse)
async def voice_chat(
    req: VoiceRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        if not req.transcript.strip():
            raise HTTPException(400, "Empty transcript")

        check_and_update_usage(user, db, is_voice=True)

        emotion_data = detect_emotion(req.transcript)
        emotion      = emotion_data["emotion"]
        user_ctx     = build_user_context(user)
        system       = build_system(
            "voice", req.scenario, req.difficulty,
            emotion, req.language, user_ctx
        )

        messages = [{"role": m.role, "content": m.content} for m in req.history[-6:]]
        messages.append({"role": "user", "content": req.transcript})

        raw, provider_used = await call_ai(system, messages)

        # Strip any leftover tags from voice reply
        clean = raw
        for tag in ["[GRAMMAR:", "[VOCAB:", "[FLUENCY:"]:
            if tag in clean:
                try:
                    s = clean.index(tag); e = clean.index("]", s)
                    clean = clean.replace(clean[s:e+1], "").strip()
                except Exception:
                    pass

        user.xp_points += 8
        db.commit()

        session = get_or_create_session(user.id, req.session_id, "voice", req.language, db)
        db.add(AmyMessage(session_id=session.id, user_id=user.id, role="user",
                          content=req.transcript, is_voice=True))
        db.add(AmyMessage(session_id=session.id, user_id=user.id, role="assistant",
                          content=clean.strip(), mood=get_mood(emotion),
                          provider=provider_used, xp_earned=8, is_voice=True))
        db.commit()

        return VoiceResponse(
            reply            = clean.strip(),
            detected_emotion = f"{emotion_data['emoji']} {emotion_data['label']}",
            mood             = get_mood(emotion),
            provider         = provider_used,
            xp_earned        = 8,
            session_id       = session.id,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Voice error: {str(e)}")


@router.get("/sessions")
def get_sessions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = db.query(AmySession).filter(
        AmySession.user_id == user.id
    ).order_by(AmySession.updated_at.desc()).limit(20).all()
    return [{
        "id": s.id, "mode": s.mode, "language": s.language,
        "title": s.title, "created_at": s.created_at.isoformat(),
        "message_count": len(s.messages),
    } for s in sessions]


@router.get("/sessions/{session_id}")
def get_session_messages(
    session_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(AmySession).filter(
        AmySession.id == session_id, AmySession.user_id == user.id
    ).first()
    if not session:
        raise HTTPException(404, "Session not found")
    return {
        "session": {"id": session.id, "mode": session.mode, "language": session.language},
        "messages": [{"role": m.role, "content": m.content, "mood": m.mood,
                      "created_at": m.created_at.isoformat()} for m in session.messages],
    }


@router.post("/vocab/save")
def save_vocab(
    req: SaveVocabRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.query(SavedVocab).filter(
        SavedVocab.user_id == user.id, SavedVocab.word == req.word
    ).first()
    if existing:
        return {"message": "Already saved"}
    db.add(SavedVocab(user_id=user.id, word=req.word,
                      definition=req.definition, example=req.example))
    db.commit()
    return {"message": "Saved"}


@router.get("/vocab")
def get_vocab(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    words = db.query(SavedVocab).filter(
        SavedVocab.user_id == user.id
    ).order_by(SavedVocab.created_at.desc()).all()
    return [{"id": w.id, "word": w.word, "definition": w.definition,
             "example": w.example} for w in words]


@router.delete("/vocab/{vocab_id}")
def delete_vocab(
    vocab_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    v = db.query(SavedVocab).filter(
        SavedVocab.id == vocab_id, SavedVocab.user_id == user.id
    ).first()
    if not v:
        raise HTTPException(404, "Not found")
    db.delete(v); db.commit()
    return {"message": "Deleted"}


@router.get("/usage")
def get_usage(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today = date.today()
    last_reset = user.last_usage_reset.date() if user.last_usage_reset else None
    if last_reset != today:
        return {
            "messages_used": 0, "messages_limit": AMY_FREE_DAILY_LIMIT,
            "voice_used": 0,    "voice_limit": AMY_FREE_VOICE_LIMIT,
            "plan": user.subscription_plan,
            "is_paid": user.subscription_plan in ("basic","pro","premium"),
        }
    is_paid = user.subscription_plan in ("basic","pro","premium")
    return {
        "messages_used":  user.amy_messages_today,
        "messages_limit": 9999 if is_paid else AMY_FREE_DAILY_LIMIT,
        "voice_used":     user.amy_voice_today,
        "voice_limit":    9999 if is_paid else AMY_FREE_VOICE_LIMIT,
        "plan":           user.subscription_plan,
        "is_paid":        is_paid,
    }


@router.get("/status")
def get_status():
    """Check which AI providers are active."""
    return get_provider_status()


@router.get("/scenarios")
def get_scenarios():
    return [
        {"id":"airport",    "icon":"🛫","name":"Airport",          "desc":"Check-in, customs, directions"},
        {"id":"interview",  "icon":"💼","name":"Job Interview",    "desc":"Mock interview practice"},
        {"id":"doctor",     "icon":"🏥","name":"Doctor Visit",     "desc":"Medical conversation"},
        {"id":"shopping",   "icon":"🛒","name":"Shopping",         "desc":"Buying, bargaining, returning"},
        {"id":"phone",      "icon":"📞","name":"Phone Call",       "desc":"Professional phone etiquette"},
        {"id":"restaurant", "icon":"🍽️","name":"Restaurant",       "desc":"Ordering and dining"},
        {"id":"meeting",    "icon":"🤝","name":"Business Meeting",  "desc":"Professional discussions"},
        {"id":"friends",    "icon":"👥","name":"Making Friends",    "desc":"Small talk and socializing"},
    ]


@router.get("/topics")
def get_topics():
    return [
        {"icon":"🌍","label":"Travel",      "prompt":"Let's practice travel English! Tell me about a place you'd love to visit."},
        {"icon":"🍕","label":"Food",        "prompt":"Let's talk about food! What's your favorite meal and why?"},
        {"icon":"🎬","label":"Movies",      "prompt":"Let's discuss movies! Tell me about a film you watched recently."},
        {"icon":"💼","label":"Work",        "prompt":"Let's practice work English! Describe your ideal job."},
        {"icon":"🏃","label":"Fitness",     "prompt":"Let's talk about health! Do you exercise regularly?"},
        {"icon":"📱","label":"Technology",  "prompt":"Let's discuss technology! How has your phone changed your life?"},
        {"icon":"🌿","label":"Environment", "prompt":"Let's talk about the environment! What do you do to help the planet?"},
        {"icon":"🎓","label":"Education",   "prompt":"Let's discuss education! What's the best way to learn a new skill?"},
    ]
