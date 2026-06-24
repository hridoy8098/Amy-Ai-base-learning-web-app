"""
Progression Engine - Handles level unlocking, prerequisites, progression tracking
"""

from sqlalchemy.orm import Session
from models.game_models import (
    GameLevel, LevelProgress, TopicProgress, SubjectProgress, 
    GameUserProgress, LevelLock, GameTopic
)
from sqlalchemy import func
from datetime import datetime


class ProgressionEngine:
    """Manages game progression logic"""
    
    @staticmethod
    def get_next_level(current_level_id: int, db: Session):
        """Get next level in topic"""
        current = db.query(GameLevel).filter(GameLevel.id == current_level_id).first()
        if not current:
            return None
        
        next_level = db.query(GameLevel).filter(
            GameLevel.topic_id == current.topic_id,
            GameLevel.level_number > current.level_number,
            GameLevel.is_active == True
        ).order_by(GameLevel.level_number).first()
        
        return next_level
    
    @staticmethod
    def check_level_unlocked(user_id: int, level_id: int, db: Session) -> bool:
        """Check if user can play this level"""
        level = db.query(GameLevel).filter(GameLevel.id == level_id).first()
        if not level:
            return False
        
        # If first level, auto unlock
        if level.level_number == 1:
            return True
        
        # Check prerequisites
        locks = db.query(LevelLock).filter(
            LevelLock.level_id == level_id
        ).all()
        
        if not locks:
            return True  # No prerequisites
        
        for lock in locks:
            # Check if prerequisite level is passed
            prerequisite_progress = db.query(LevelProgress).filter(
                LevelProgress.user_id == user_id,
                LevelProgress.level_id == lock.prerequisite_level_id,
                LevelProgress.is_passed == True
            ).first()
            
            if not prerequisite_progress:
                return False
        
        return True
    
    @staticmethod
    def unlock_next_levels(user_id: int, completed_level_id: int, db: Session):
        """Auto-unlock next level when current is completed"""
        current_level = db.query(GameLevel).filter(
            GameLevel.id == completed_level_id
        ).first()
        
        if not current_level:
            return
        
        # Get next level
        next_level = ProgressionEngine.get_next_level(completed_level_id, db)
        if next_level:
            # Check again in case there are specific prerequisites
            if ProgressionEngine.check_level_unlocked(user_id, next_level.id, db):
                # Init level progress if not exists
                level_prog = db.query(LevelProgress).filter(
                    LevelProgress.user_id == user_id,
                    LevelProgress.level_id == next_level.id
                ).first()
                
                if not level_prog:
                    level_prog = LevelProgress(
                        user_id=user_id,
                        level_id=next_level.id,
                        is_unlocked=True
                    )
                    db.add(level_prog)
                    db.commit()
    
    @staticmethod
    def update_level_progress(
        user_id: int, 
        level_id: int, 
        is_passed: bool, 
        stars: int, 
        score: float,
        db: Session
    ):
        """Update level progress after attempt"""
        level_progress = db.query(LevelProgress).filter(
            LevelProgress.user_id == user_id,
            LevelProgress.level_id == level_id
        ).first()
        
        if not level_progress:
            level_progress = LevelProgress(
                user_id=user_id,
                level_id=level_id
            )
            db.add(level_progress)
        
        level_progress.attempts += 1
        level_progress.best_score = max(level_progress.best_score, score)
        level_progress.best_stars = max(level_progress.best_stars, stars)
        
        if is_passed:
            level_progress.is_passed = True
            level_progress.passed_at = datetime.utcnow()
        
        db.commit()
        
        # Unlock next level
        if is_passed:
            ProgressionEngine.unlock_next_levels(user_id, level_id, db)
    
    @staticmethod
    def calculate_topic_mastery(user_id: int, topic_id: int, db: Session) -> float:
        """Calculate mastery percentage for topic (0-100)"""
        levels = db.query(GameLevel).filter(
            GameLevel.topic_id == topic_id,
            GameLevel.is_active == True
        ).count()
        
        if levels == 0:
            return 0.0
        
        passed = db.query(LevelProgress).filter(
            LevelProgress.user_id == user_id,
            GameLevel.topic_id == topic_id,
            LevelProgress.is_passed == True
        ).join(GameLevel).count()
        
        return (passed / levels) * 100
    
    @staticmethod
    def calculate_subject_mastery(user_id: int, subject_id: int, db: Session) -> float:
        """Calculate mastery percentage for subject (0-100)"""
        from models.game_models import GameSubject
        
        # Get all topics in subject
        topics = db.query(GameTopic).filter(
            GameTopic.subject_id == subject_id,
            GameTopic.is_active == True
        ).all()
        
        if not topics:
            return 0.0
        
        total_mastery = 0
        for topic in topics:
            mastery = ProgressionEngine.calculate_topic_mastery(user_id, topic.id, db)
            total_mastery += mastery
        
        return total_mastery / len(topics)
    
    @staticmethod
    def init_user_progress(user_id: int, db: Session):
        """Initialize user progress entry"""
        existing = db.query(GameUserProgress).filter(
            GameUserProgress.user_id == user_id
        ).first()
        
        if not existing:
            user_progress = GameUserProgress(
                user_id=user_id,
                current_hearts=3,
                current_xp=0,
                current_streak=0
            )
            db.add(user_progress)
            db.commit()
    
    @staticmethod
    def get_user_overall_progress(user_id: int, db: Session):
        """Get user's overall game progress"""
        user_progress = db.query(GameUserProgress).filter(
            GameUserProgress.user_id == user_id
        ).first()
        
        if not user_progress:
            ProgressionEngine.init_user_progress(user_id, db)
            user_progress = db.query(GameUserProgress).filter(
                GameUserProgress.user_id == user_id
            ).first()
        
        # Calculate total mastery
        subjects = db.query(GameSubject).filter(
            GameSubject.is_active == True
        ).all()
        
        total_mastery = 0
        for subject in subjects:
            mastery = ProgressionEngine.calculate_subject_mastery(user_id, subject.id, db)
            total_mastery += mastery
        
        avg_mastery = total_mastery / len(subjects) if subjects else 0
        
        return {
            "user_id": user_id,
            "total_xp": user_progress.current_xp,
            "hearts": user_progress.current_hearts,
            "streak": user_progress.current_streak,
            "tier": user_progress.user_tier,
            "overall_mastery": round(avg_mastery, 2),
            "completed_levels": db.query(LevelProgress).filter(
                LevelProgress.user_id == user_id,
                LevelProgress.is_passed == True
            ).count(),
            "total_attempts": db.query(LevelProgress).filter(
                LevelProgress.user_id == user_id
            ).count()
        }


from models.game_models import GameSubject
