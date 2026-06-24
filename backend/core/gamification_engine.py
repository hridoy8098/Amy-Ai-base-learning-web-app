"""
Gamification Engine - Handles XP, Hearts, Streaks, Rewards, Badges
"""

import math
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.game_models import (
    GameUserProgress, LevelProgress, UserGameBadge, 
    GameBadge, Leaderboard, RewardChest, DailyMission, UserDailyMission
)


class GamificationEngine:
    """Manages game mechanics: XP, hearts, streaks, rewards"""
    
    # ═══════════════════════════════════════════════════════════════════════════
    # XP CALCULATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    @staticmethod
    def calculate_xp(
        base_xp: int,
        is_correct: bool = True,
        combo_count: int = 0,
        streak_continue: bool = False,
        perfect_level: bool = False,
        confidence_level: str = "sure",
        difficulty: str = "medium"
    ) -> int:
        """
        Calculate total XP earned
        - Base XP from level
        - Combo bonus (5+ correct in row)
        - Streak bonus
        - Perfect level bonus (all correct)
        - Confidence bonus (answered confidently)
        - Difficulty multiplier
        """
        if not is_correct:
            return 0
        
        total_xp = base_xp
        
        # Difficulty multiplier
        difficulty_mult = {
            "easy": 1.0,
            "medium": 1.2,
            "hard": 1.5
        }.get(difficulty, 1.0)
        
        total_xp = int(total_xp * difficulty_mult)
        
        # Combo bonus
        if combo_count >= 5:
            combo_bonus = 50 + (combo_count - 5) * 5
            total_xp += combo_bonus
        
        # Streak bonus
        if streak_continue:
            total_xp += 25
        
        # Perfect level bonus
        if perfect_level:
            total_xp += 50
        
        # Confidence bonus
        if confidence_level == "very_sure":
            total_xp += 25
        elif confidence_level == "sure":
            total_xp += 10
        
        return total_xp
    
    # ═══════════════════════════════════════════════════════════════════════════
    # HEARTS SYSTEM
    # ═══════════════════════════════════════════════════════════════════════════
    
    @staticmethod
    def lose_heart(user_id: int, db: Session) -> int:
        """Subtract 1 heart, return remaining"""
        user_prog = db.query(GameUserProgress).filter(
            GameUserProgress.user_id == user_id
        ).first()
        
        if user_prog:
            user_prog.current_hearts = max(0, user_prog.current_hearts - 1)
            db.commit()
            return user_prog.current_hearts
        
        return 0
    
    @staticmethod
    def restore_hearts(user_id: int, amount: int = 3, db: Session = None):
        """Restore hearts to max"""
        if db is None:
            return
        
        user_prog = db.query(GameUserProgress).filter(
            GameUserProgress.user_id == user_id
        ).first()
        
        if user_prog:
            user_prog.current_hearts = amount
            db.commit()
    
    @staticmethod
    def get_hearts(user_id: int, db: Session) -> int:
        """Get current hearts"""
        user_prog = db.query(GameUserProgress).filter(
            GameUserProgress.user_id == user_id
        ).first()
        
        return user_prog.current_hearts if user_prog else 3
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STREAK SYSTEM
    # ═══════════════════════════════════════════════════════════════════════════
    
    @staticmethod
    def increment_streak(user_id: int, db: Session) -> int:
        """Increment streak, return new streak count"""
        user_prog = db.query(GameUserProgress).filter(
            GameUserProgress.user_id == user_id
        ).first()
        
        if user_prog:
            user_prog.current_streak += 1
            user_prog.max_streak = max(user_prog.max_streak, user_prog.current_streak)
            db.commit()
            return user_prog.current_streak
        
        return 0
    
    @staticmethod
    def reset_streak(user_id: int, db: Session):
        """Reset streak on failure"""
        user_prog = db.query(GameUserProgress).filter(
            GameUserProgress.user_id == user_id
        ).first()
        
        if user_prog:
            user_prog.current_streak = 0
            db.commit()
    
    @staticmethod
    def get_streak(user_id: int, db: Session) -> dict:
        """Get streak info"""
        user_prog = db.query(GameUserProgress).filter(
            GameUserProgress.user_id == user_id
        ).first()
        
        if user_prog:
            return {
                "current": user_prog.current_streak,
                "max": user_prog.max_streak
            }
        
        return {"current": 0, "max": 0}
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STAR RATING
    # ═══════════════════════════════════════════════════════════════════════════
    
    @staticmethod
    def calculate_stars(
        score: float,
        time_used: int,
        time_limit: int,
        perfect: bool = False
    ) -> int:
        """
        Calculate stars earned
        - 3 stars: 90%+ score + within time limit
        - 2 stars: 70-89% score
        - 1 star: 50-69% score
        - 0 stars: <50% score
        """
        if score >= 90 and time_used <= time_limit and perfect:
            return 3
        elif score >= 90 and time_used <= time_limit:
            return 3
        elif score >= 70:
            return 2
        elif score >= 50:
            return 1
        else:
            return 0
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TIER SYSTEM
    # ═══════════════════════════════════════════════════════════════════════════
    
    @staticmethod
    def get_tier_for_xp(total_xp: int) -> str:
        """Get tier based on total XP"""
        if total_xp >= 10000:
            return "diamond"
        elif total_xp >= 5000:
            return "gold"
        elif total_xp >= 1000:
            return "silver"
        else:
            return "bronze"
    
    @staticmethod
    def update_tier(user_id: int, db: Session):
        """Update user tier based on total XP"""
        user_prog = db.query(GameUserProgress).filter(
            GameUserProgress.user_id == user_id
        ).first()
        
        if user_prog:
            new_tier = GamificationEngine.get_tier_for_xp(user_prog.current_xp)
            user_prog.user_tier = new_tier
            db.commit()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BADGES & ACHIEVEMENTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    @staticmethod
    def award_badge(user_id: int, badge_id: int, db: Session) -> bool:
        """Award badge to user if not already owned"""
        existing = db.query(UserGameBadge).filter(
            UserGameBadge.user_id == user_id,
            UserGameBadge.game_badge_id == badge_id
        ).first()
        
        if not existing:
            user_badge = UserGameBadge(
                user_id=user_id,
                game_badge_id=badge_id,
                earned_at=datetime.utcnow()
            )
            db.add(user_badge)
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def check_achievements(user_id: int, db: Session) -> list:
        """
        Check for badge achievements unlocked
        - First Level Complete
        - 5 Streak
        - 100 XP Earned
        - Perfect Score
        - etc.
        """
        badges_earned = []
        
        # Get user progress
        user_prog = db.query(GameUserProgress).filter(
            GameUserProgress.user_id == user_id
        ).first()
        
        if not user_prog:
            return []
        
        # Get user's badges
        user_badges = db.query(UserGameBadge).filter(
            UserGameBadge.user_id == user_id
        ).all()
        
        owned_badge_ids = [b.game_badge_id for b in user_badges]
        
        # Check badges
        checks = [
            # First level
            (1, lambda: db.query(LevelProgress).filter(
                LevelProgress.user_id == user_id,
                LevelProgress.is_passed == True
            ).count() >= 1, "First Level"),
            
            # Streak badges
            (2, lambda: user_prog.current_streak >= 5, "5-Day Streak"),
            (3, lambda: user_prog.current_streak >= 30, "30-Day Streak"),
            
            # XP badges
            (4, lambda: user_prog.current_xp >= 100, "100 XP Earned"),
            (5, lambda: user_prog.current_xp >= 1000, "1000 XP Earned"),
            
            # Perfect score
            (6, lambda: db.query(LevelProgress).filter(
                LevelProgress.user_id == user_id,
                LevelProgress.best_stars == 3
            ).count() >= 5, "5 Perfect Scores"),
        ]
        
        for badge_id, condition, name in checks:
            if badge_id not in owned_badge_ids and condition():
                if GamificationEngine.award_badge(user_id, badge_id, db):
                    badges_earned.append({"badge_id": badge_id, "name": name})
        
        return badges_earned
    
    # ═══════════════════════════════════════════════════════════════════════════
    # LEADERBOARD
    # ═══════════════════════════════════════════════════════════════════════════
    
    @staticmethod
    def update_leaderboard(user_id: int, db: Session):
        """Update leaderboard rankings"""
        user_prog = db.query(GameUserProgress).filter(
            GameUserProgress.user_id == user_id
        ).first()
        
        if not user_prog:
            return
        
        periods = ["weekly", "monthly", "all_time"]
        
        for period in periods:
            # Calculate timeframe
            if period == "weekly":
                since = datetime.utcnow() - timedelta(days=7)
            elif period == "monthly":
                since = datetime.utcnow() - timedelta(days=30)
            else:
                since = None
            
            # Get or create leaderboard entry
            leaderboard = db.query(Leaderboard).filter(
                Leaderboard.user_id == user_id,
                Leaderboard.period == period
            ).first()
            
            if not leaderboard:
                leaderboard = Leaderboard(
                    user_id=user_id,
                    period=period,
                    total_xp=0,
                    rank=0
                )
                db.add(leaderboard)
            
            # Update XP
            leaderboard.total_xp = user_prog.current_xp
            leaderboard.updated_at = datetime.utcnow()
            
            db.commit()
            
            # Calculate rank
            if period == "weekly":
                since = datetime.utcnow() - timedelta(days=7)
            elif period == "monthly":
                since = datetime.utcnow() - timedelta(days=30)
            else:
                since = None
            
            if since:
                higher_xp = db.query(Leaderboard).filter(
                    Leaderboard.period == period,
                    Leaderboard.total_xp > leaderboard.total_xp,
                    Leaderboard.updated_at >= since
                ).count()
            else:
                higher_xp = db.query(Leaderboard).filter(
                    Leaderboard.period == period,
                    Leaderboard.total_xp > leaderboard.total_xp
                ).count()
            
            leaderboard.rank = higher_xp + 1
            db.commit()
    
    @staticmethod
    def get_leaderboard(period: str = "weekly", limit: int = 100, db: Session = None):
        """Get leaderboard"""
        if db is None:
            return []
        
        leaderboard = db.query(Leaderboard).filter(
            Leaderboard.period == period
        ).order_by(Leaderboard.total_xp.desc()).limit(limit).all()
        
        return [
            {
                "rank": idx + 1,
                "user_id": entry.user_id,
                "total_xp": entry.total_xp
            }
            for idx, entry in enumerate(leaderboard)
        ]
    
    # ═══════════════════════════════════════════════════════════════════════════
    # REWARDS
    # ═══════════════════════════════════════════════════════════════════════════
    
    @staticmethod
    def award_xp(user_id: int, xp_amount: int, db: Session):
        """Award XP to user"""
        user_prog = db.query(GameUserProgress).filter(
            GameUserProgress.user_id == user_id
        ).first()
        
        if user_prog:
            user_prog.current_xp += xp_amount
            db.commit()
            
            # Update tier
            GamificationEngine.update_tier(user_id, db)
            
            # Update leaderboard
            GamificationEngine.update_leaderboard(user_id, db)
            
            # Check for achievements
            GamificationEngine.check_achievements(user_id, db)
    
    @staticmethod
    def award_reward_chest(user_id: int, chest_type: str = "bronze", db: Session = None):
        """Award reward chest to user"""
        if db is None:
            return
        
        chest = RewardChest(
            user_id=user_id,
            chest_type=chest_type,
            is_opened=False,
            created_at=datetime.utcnow()
        )
        db.add(chest)
        db.commit()
