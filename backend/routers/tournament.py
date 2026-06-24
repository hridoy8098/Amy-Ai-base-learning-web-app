"""
Feature #11 — Weekly Tournament
সবচেয়ে বেশি XP = prize। Competition motivation তৈরি করে।
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from models.models import User
from datetime import datetime, timedelta

router = APIRouter()

def get_week_bounds():
    today = datetime.utcnow()
    start = today - timedelta(days=today.weekday())
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=7)
    return start, end

@router.get("/current")
def current_tournament(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    start, end = get_week_bounds()
    top_users = db.query(User).filter(User.is_active == True).order_by(User.xp_points.desc()).limit(20).all()
    leaderboard = []
    user_rank = None
    for i, u in enumerate(top_users):
        entry = {"rank": i+1, "name": u.name, "avatar": u.avatar, "xp": u.xp_points, "level": u.level}
        leaderboard.append(entry)
        if u.id == user.id:
            user_rank = i + 1

    prizes = [
        {"rank": 1, "prize": "🥇 Gold Badge + 500 XP + 1 Month Pro"},
        {"rank": 2, "prize": "🥈 Silver Badge + 300 XP"},
        {"rank": 3, "prize": "🥉 Bronze Badge + 150 XP"},
        {"rank": "4-10", "prize": "⭐ 50 XP Bonus"},
    ]
    return {
        "week_start": start.isoformat(),
        "week_end": end.isoformat(),
        "leaderboard": leaderboard,
        "your_rank": user_rank,
        "your_xp": user.xp_points,
        "prizes": prizes,
        "days_left": (end - datetime.utcnow()).days
    }

@router.get("/history")
def tournament_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"past_tournaments": [], "best_rank": None, "total_prizes_won": 0}
