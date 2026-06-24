"""
Feature #25 — Amy Memory System
আগের কথোপকথন মনে রেখে personal relationship তৈরি করবে।
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from core.ai_providers import call_ai
from models.models import User, AmyMessage, UserMemory
import json, re

router = APIRouter()

class MemoryUpdate(BaseModel):
    category: str
    key: str
    value: str

@router.get("/")
def get_memories(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    memories = db.query(UserMemory).filter(UserMemory.user_id == user.id).all()
    grouped = {}
    for m in memories:
        if m.category not in grouped: grouped[m.category] = []
        grouped[m.category].append({"id": m.id, "key": m.key, "value": m.value})
    return {"memories": grouped, "total": len(memories)}

@router.post("/extract")
async def extract_memories(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Recent conversations থেকে memory extract করে save করে।"""
    recent = db.query(AmyMessage).filter(
        AmyMessage.user_id == user.id, AmyMessage.role == "user"
    ).order_by(AmyMessage.created_at.desc()).limit(20).all()

    if not recent:
        return {"message": "No conversations found to extract memories from.", "extracted": 0}

    msgs_text = [m.content for m in recent]
    system = (
        "Extract important personal information from these user messages to remember for future conversations. "
        "Return ONLY valid JSON:\n"
        '{"memories":[{"category":"interest","key":"favorite_topic","value":"technology"}]}\n'
        "Categories: interest, goal, weakness, achievement, personal, preference\n"
        "Extract max 10 important facts."
    )
    ai_msgs = [{"role": "user", "content": f"Extract memories from: {json.dumps(msgs_text)}"}]

    try:
        raw, _ = await call_ai(system, ai_msgs)
        m = re.search(r'\{.*\}', raw.strip(), re.DOTALL)
        if m:
            data = json.loads(m.group())
            count = 0
            for mem in data.get("memories", [])[:10]:
                existing = db.query(UserMemory).filter(
                    UserMemory.user_id == user.id,
                    UserMemory.category == mem.get("category"),
                    UserMemory.key == mem.get("key")
                ).first()
                if existing:
                    existing.value = mem.get("value", "")
                else:
                    db.add(UserMemory(user_id=user.id, category=mem.get("category", "personal"), key=mem.get("key", "fact"), value=mem.get("value", "")))
                    count += 1
            db.commit()
            return {"message": f"Extracted {count} new memories!", "extracted": count}
    except:
        pass
    return {"message": "Memory extraction complete.", "extracted": 0}

@router.post("/add")
def add_memory(req: MemoryUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(UserMemory).filter(UserMemory.user_id == user.id, UserMemory.category == req.category, UserMemory.key == req.key).first()
    if existing:
        existing.value = req.value
    else:
        db.add(UserMemory(user_id=user.id, category=req.category, key=req.key, value=req.value))
    db.commit()
    return {"message": "Memory saved!"}

@router.delete("/{memory_id}")
def delete_memory(memory_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    m = db.query(UserMemory).filter(UserMemory.id == memory_id, UserMemory.user_id == user.id).first()
    if not m:
        from fastapi import HTTPException
        raise HTTPException(404, "Not found")
    db.delete(m); db.commit()
    return {"message": "Deleted"}

def get_user_memory_context(user_id: int, db: Session) -> str:
    """Amy chat-এ use করার জন্য memory context।"""
    memories = db.query(UserMemory).filter(UserMemory.user_id == user_id).all()
    if not memories: return ""
    lines = [f"- {m.category}/{m.key}: {m.value}" for m in memories[:15]]
    return "\n\nAmy's Memory about this user:\n" + "\n".join(lines)