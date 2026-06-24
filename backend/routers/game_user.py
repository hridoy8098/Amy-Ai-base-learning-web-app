"""
Game Learning System - User Router
Player gameplay endpoints

GET    /api/game/subjects                 - List subjects
GET    /api/game/subjects/{id}/topics     - List topics with progress
GET    /api/game/topics/{id}/levels       - List levels with progress
POST   /api/game/levels/{id}/start        - Start level
POST   /api/game/attempts/{id}/answer     - Submit answer
POST   /api/game/attempts/{id}/complete   - Complete level
GET    /api/game/user/progress            - Get user progress
GET    /api/game/user/weak-areas          - Get weak areas
GET    /api/game/leaderboard              - Get leaderboard
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from core.database import get_db
from core.security import get_current_user
from models.game_models import (
    GameSubject, GameTopic, GameLevel, GameQuestion, FallbackQuestion,
    GameUserProgress, TopicProgress, LevelProgress, LevelAttempt,
    QuestionResponse, WeakArea, Leaderboard, UserTierEnum, SubjectProgress
)
from models.models import User
from typing import Optional, List
from datetime import datetime, timedelta
import random

router = APIRouter(
    tags=["game-player"]
)

# ═══════════════════════════════════════════════════════════════════════════
# HELPER: Get current user
# ═══════════════════════════════════════════════════════════════════════════

# get_current_user is already imported from core.security


# ═══════════════════════════════════════════════════════════════════════════
# PROGRESSION VIEW ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/subjects")
async def list_subjects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all subjects with user progress"""
    
    subjects = db.query(GameSubject).filter(GameSubject.is_active == True).order_by(
        GameSubject.order_index
    ).all()
    
    result = []
    for subject in subjects:
        # Get user's progress for this subject
        progress = db.query(SubjectProgress).filter(
            SubjectProgress.user_id == current_user.id,
            SubjectProgress.subject_id == subject.id
        ).first()
        
        result.append({
            "id": subject.id,
            "name": subject.name,
            "icon": subject.icon,
            "color": subject.color,
            "topic_count": len(subject.topics),
            "xp_earned": progress.xp_earned if progress else 0,
            "last_attempted": progress.last_attempted_at if progress else None
        })
    
    return {
        "total": len(result),
        "subjects": result
    }


@router.get("/subjects/{subject_id}/topics")
async def list_topics_with_progress(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List topics for subject with user progress"""
    
    subject = db.query(GameSubject).filter(GameSubject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    topics = db.query(GameTopic).filter(
        GameTopic.subject_id == subject_id,
        GameTopic.is_active == True
    ).order_by(GameTopic.order_index).all()
    
    result = []
    for topic in topics:
        progress = db.query(TopicProgress).filter(
            TopicProgress.user_id == current_user.id,
            TopicProgress.topic_id == topic.id
        ).first()
        
        result.append({
            "id": topic.id,
            "name": topic.name,
            "icon": topic.icon,
            "level_count": len(topic.levels),
            "mastery_score": progress.mastery_score if progress else 0.0,
            "xp_earned": progress.xp_earned if progress else 0,
            "weakness_detected": progress.weakness_detected if progress else False
        })
    
    return {
        "subject": subject.name,
        "total": len(result),
        "topics": result
    }


@router.get("/topics/{topic_id}/levels")
async def list_levels_with_progress(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List levels for topic (progression map)"""
    
    topic = db.query(GameTopic).filter(GameTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    levels = db.query(GameLevel).filter(
        GameLevel.topic_id == topic_id,
        GameLevel.is_active == True
    ).order_by(GameLevel.level_number).all()
    
    result = []
    for level in levels:
        progress = db.query(LevelProgress).filter(
            LevelProgress.user_id == current_user.id,
            LevelProgress.level_id == level.id
        ).first()
        
        # Determine level state
        if not progress:
            state = "locked"  # Not attempted
            if level.level_number == 1:  # First level is always unlocked
                state = "unlocked"
        elif progress.is_passed:
            state = "completed"
        elif progress.is_unlocked:
            state = "in_progress"
        else:
            state = "locked"
        
        result.append({
            "id": level.id,
            "level_number": level.level_number,
            "title": level.title,
            "difficulty": level.difficulty,
            "level_type": level.level_type,
            "state": state,
            "best_score": progress.best_score if progress else 0,
            "stars": progress.best_stars if progress else 0,
            "attempts": progress.attempts if progress else 0,
            "is_locked": state == "locked"
        })
    
    return {
        "topic": topic.name,
        "total": len(result),
        "levels": result
    }


# ═══════════════════════════════════════════════════════════════════════════
# GAMEPLAY ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/levels/{level_id}/start")
async def start_level(
    level_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a level - initialize attempt"""
    
    level = db.query(GameLevel).filter(GameLevel.id == level_id).first()
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    
    # Check if user can play this level
    level_prog = db.query(LevelProgress).filter(
        LevelProgress.user_id == current_user.id,
        LevelProgress.level_id == level_id
    ).first()
    
    if not level_prog:
        # First attempt on this level
        if level.level_number != 1:
            # Check prerequisite
            raise HTTPException(status_code=403, detail="Level is locked. Complete previous levels first.")
        
        # Create progress entry
        level_prog = LevelProgress(
            user_id=current_user.id,
            level_id=level_id,
            is_unlocked=True,
            unlock_date=datetime.now()
        )
        db.add(level_prog)
        db.commit()
    
    elif not level_prog.is_unlocked:
        raise HTTPException(status_code=403, detail="Level is locked")
    
    # Get questions for this level
    # Strategy: Get fallback questions first, then AI-generated, then random mix
    fallback_qs = db.query(FallbackQuestion).filter(
        FallbackQuestion.level_id == level_id,
        FallbackQuestion.is_active == True
    ).order_by(desc(FallbackQuestion.priority)).all()
    
    ai_qs = db.query(GameQuestion).filter(
        GameQuestion.level_id == level_id,
        GameQuestion.is_active == True
    ).all()
    
    # Mix them and get required count
    all_qs = fallback_qs[:level.question_count] + ai_qs[:(level.question_count - len(fallback_qs))]
    
    if len(all_qs) < level.question_count:
        raise HTTPException(status_code=500, detail="Not enough questions for this level")
    
    random.shuffle(all_qs)
    selected_qs = all_qs[:level.question_count]
    
    # Create attempt record
    attempt = LevelAttempt(
        user_id=current_user.id,
        level_id=level_id,
        started_at=datetime.now(),
        question_ids=[q.id for q in selected_qs],
        hearts_used=0
    )
    
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    # Get user's hearts
    user_prog = db.query(GameUserProgress).filter(
        GameUserProgress.user_id == current_user.id
    ).first()
    
    return {
        "attempt_id": attempt.id,
        "level": {
            "id": level.id,
            "title": level.title,
            "difficulty": level.difficulty,
            "question_count": len(selected_qs),
            "time_limit": level.time_limit_seconds,
            "pass_score": level.pass_score
        },
        "questions": [
            {
                "id": q.id,
                "type": q.question_type,
                "text": q.question_text,
                "media": q.question_media,
                "options": q.options  # For MCQ type
            }
            if isinstance(q, GameQuestion) else
            {
                "id": q.id,
                "type": q.question_type,
                "text": q.question_text,
                "media": None,
                "options": q.options
            }
            for q in selected_qs
        ],
        "hearts": user_prog.current_hearts if user_prog else 3,
        "started_at": attempt.started_at.isoformat()
    }


@router.post("/attempts/{attempt_id}/answer")
async def submit_answer(
    attempt_id: int,
    question_id: int,
    user_answer: dict,
    time_taken_seconds: int = 0,
    confidence_level: str = "sure",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit answer for a question"""
    
    # Get attempt
    attempt = db.query(LevelAttempt).filter(
        LevelAttempt.id == attempt_id,
        LevelAttempt.user_id == current_user.id
    ).first()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    # Get question
    question = db.query(GameQuestion).filter(GameQuestion.id == question_id).first()
    if not question:
        question = db.query(FallbackQuestion).filter(FallbackQuestion.id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check answer
    is_correct = check_answer(user_answer, question.correct_answer, question.question_type)
    
    # Record response
    response = QuestionResponse(
        attempt_id=attempt_id,
        question_id=question_id,
        user_answer=user_answer,
        is_correct=is_correct,
        time_taken_seconds=time_taken_seconds,
        confidence_level=confidence_level
    )
    
    db.add(response)
    
    # Update attempt
    attempt.questions_attempted += 1
    if is_correct:
        attempt.questions_correct += 1
        attempt.combo_count += 1
    else:
        attempt.hearts_used += 1
        attempt.combo_count = 0
    
    # Add confidence bonus tracking
    if confidence_level == "very_sure":
        attempt.confident_answers += 1
    elif confidence_level == "unsure":
        attempt.unsure_answers += 1
    
    db.commit()
    
    return {
        "is_correct": is_correct,
        "combo_count": attempt.combo_count,
        "hearts_used": attempt.hearts_used,
        "questions_attempted": attempt.questions_attempted,
        "feedback": "✅ Correct!" if is_correct else "❌ Not correct",
        "explanation": question.explanation if hasattr(question, 'explanation') else None
    }


@router.post("/attempts/{attempt_id}/complete")
async def complete_level(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete level attempt - calculate results and rewards"""
    
    # Get attempt
    attempt = db.query(LevelAttempt).filter(
        LevelAttempt.id == attempt_id,
        LevelAttempt.user_id == current_user.id
    ).first()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    if attempt.completed_at:
        raise HTTPException(status_code=400, detail="Attempt already completed")
    
    # Calculate final score
    attempt.final_score = int((attempt.questions_correct / attempt.questions_attempted) * 100) \
                          if attempt.questions_attempted > 0 else 0
    
    # Get level
    level = db.query(GameLevel).filter(GameLevel.id == attempt.level_id).first()
    
    # Determine if passed
    attempt.is_passed = attempt.final_score >= level.pass_score
    
    # Calculate stars (1-3 based on score and speed)
    if attempt.final_score >= 90:
        attempt.stars_earned = 3
    elif attempt.final_score >= 70:
        attempt.stars_earned = 2
    elif attempt.final_score >= 50:
        attempt.stars_earned = 1
    else:
        attempt.stars_earned = 0
    
    # Calculate XP
    calculate_xp_rewards(attempt, level, current_user, db)
    
    # Update level progress
    level_prog = db.query(LevelProgress).filter(
        LevelProgress.user_id == current_user.id,
        LevelProgress.level_id == level.id
    ).first()
    
    if attempt.is_passed:
        level_prog.is_passed = True
        level_prog.is_completed = True
        level_prog.completion_date = datetime.now()
        
        if attempt.stars_earned > level_prog.best_stars:
            level_prog.best_stars = attempt.stars_earned
    
    if attempt.final_score > level_prog.best_score:
        level_prog.best_score = attempt.final_score
    
    level_prog.attempts += 1
    
    # Mark completion
    attempt.completed_at = datetime.now()
    attempt.duration_seconds = int((attempt.completed_at - attempt.started_at).total_seconds())
    
    db.commit()
    
    return {
        "attempt_id": attempt_id,
        "is_passed": attempt.is_passed,
        "final_score": attempt.final_score,
        "stars_earned": attempt.stars_earned,
        "xp_earned": attempt.total_xp_earned,
        "duration_seconds": attempt.duration_seconds,
        "results": {
            "correct": attempt.questions_correct,
            "total": attempt.questions_attempted,
            "accuracy": f"{attempt.final_score}%"
        },
        "rewards": {
            "base_xp": attempt.base_xp,
            "combo_bonus": attempt.combo_bonus_xp,
            "streak_bonus": attempt.streak_bonus_xp,
            "total_xp": attempt.total_xp_earned
        }
    }


# ═══════════════════════════════════════════════════════════════════════════
# USER PROGRESS ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/user/progress")
async def get_user_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's overall game progress"""
    
    user_prog = db.query(GameUserProgress).filter(
        GameUserProgress.user_id == current_user.id
    ).first()
    
    if not user_prog:
        # Create if doesn't exist
        user_prog = GameUserProgress(user_id=current_user.id)
        db.add(user_prog)
        db.commit()
    
    return {
        "total_xp": user_prog.total_xp,
        "tier": user_prog.current_tier,
        "current_streak": user_prog.current_streak,
        "best_streak": user_prog.best_streak,
        "hearts": {
            "current": user_prog.current_hearts,
            "total": user_prog.total_hearts
        },
        "daily_mission_completed": user_prog.daily_mission_completed,
        "last_active": user_prog.last_active_at
    }


@router.get("/user/weak-areas")
async def get_weak_areas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's detected weak areas"""
    
    weak_areas = db.query(WeakArea).filter(
        WeakArea.user_id == current_user.id,
        WeakArea.is_active == True
    ).all()
    
    result = []
    for area in weak_areas:
        topic = db.query(GameTopic).filter(GameTopic.id == area.topic_id).first()
        result.append({
            "id": area.id,
            "topic": topic.name if topic else "Unknown",
            "topic_id": area.topic_id,
            "failure_count": area.failure_count,
            "next_review_date": area.next_review_date,
            "message": f"You've had {area.failure_count} failed attempts. Practice this topic!"
        })
    
    return {
        "total": len(result),
        "weak_areas": result
    }


@router.get("/leaderboard")
async def get_leaderboard(
    period: str = "weekly",  # weekly, monthly, all-time
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get leaderboard rankings"""
    
    leaders = db.query(Leaderboard).filter(
        Leaderboard.period == period
    ).order_by(Leaderboard.rank).limit(limit).all()
    
    result = []
    for leader in leaders:
        user = db.query(User).filter(User.id == leader.user_id).first()
        result.append({
            "rank": leader.rank,
            "player": user.name if user else "Unknown",
            "xp": leader.total_xp,
            "streak": leader.streak,
            "tier": leader.tier,
            "is_current_user": user.id == current_user.id
        })
    
    return {
        "period": period,
        "total": len(result),
        "leaderboard": result
    }


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def check_answer(user_answer: dict, correct_answer, question_type: str) -> bool:
    """Check if user answer is correct"""
    
    if question_type == "mcq":
        return user_answer.get("selected_option") == correct_answer
    
    elif question_type == "fill_blank":
        return user_answer.get("answer", "").lower().strip() == correct_answer.lower().strip()
    
    elif question_type == "match_pairs":
        return user_answer == correct_answer
    
    else:
        # For other types, implement accordingly
        return user_answer.get("answer") == correct_answer


def calculate_xp_rewards(attempt: LevelAttempt, level: GameLevel, user: User, db: Session):
    """Calculate and award XP with all bonuses"""
    
    # Base XP
    attempt.base_xp = level.xp_reward
    
    # Combo bonus
    if attempt.combo_count >= 5:
        attempt.combo_bonus_xp = 50
    
    # Perfect bonus (no wrong answers)
    if attempt.hearts_used == 0 and attempt.is_passed:
        attempt.perfect_bonus_xp = 50
    
    # Streak bonus
    user_prog = db.query(GameUserProgress).filter(
        GameUserProgress.user_id == user.id
    ).first()
    
    if user_prog:
        if attempt.is_passed:
            attempt.streak_bonus_xp = 25
            user_prog.current_streak += 1
        else:
            user_prog.current_streak = 0
    
    # Confidence bonus
    if attempt.confident_answers > (attempt.questions_attempted * 0.7):
        attempt.confidence_bonus_xp = 25
    
    # Final XP
    attempt.total_xp_earned = (
        attempt.base_xp +
        attempt.combo_bonus_xp +
        attempt.streak_bonus_xp +
        attempt.perfect_bonus_xp +
        attempt.confidence_bonus_xp
    )
    
    # Update user progress
    if user_prog:
        user_prog.total_xp += attempt.total_xp_earned
        user_prog.last_active_at = datetime.now()
