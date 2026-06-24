"""
Game Learning System Models
Placement Test + Duolingo-style game learning with hearts, XP, streaks, etc.
"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean,
    DateTime, Float, ForeignKey, JSON, Enum, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
import enum


# ═══════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════

class DifficultyEnum(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class LevelTypeEnum(str, enum.Enum):
    NORMAL = "normal"
    BOSS = "boss"


class QuestionTypeEnum(str, enum.Enum):
    MCQ = "mcq"
    FILL_BLANK = "fill_blank"
    MATCH_PAIRS = "match_pairs"
    SENTENCE_REORDER = "sentence_reorder"
    ERROR_CORRECTION = "error_correction"
    LISTENING = "listening"
    SPEAKING = "speaking"
    IMAGE_WORD = "image_word"
    FAST_TAP = "fast_tap"


class UserTierEnum(str, enum.Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    DIAMOND = "diamond"


class QuestionSourceEnum(str, enum.Enum):
    ADMIN_MANUAL = "admin_manual"
    AI_GENERATED = "ai_generated"


class ConfidenceLevelEnum(str, enum.Enum):
    VERY_SURE = "very_sure"
    SURE = "sure"
    UNSURE = "unsure"


class ChallengeStatusEnum(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# ═══════════════════════════════════════════════════════════════════════════
# CORE CURRICULUM TABLES
# ═══════════════════════════════════════════════════════════════════════════

class GameSubject(Base):
    """Learning subjects: Grammar, Vocabulary, Speaking, Reading, Writing"""
    __tablename__ = 'game_subjects'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    icon = Column(String(255))
    color = Column(String(7))  # Hex color
    order_index = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    topics = relationship('GameTopic', back_populates='subject', cascade='all, delete-orphan')
    __table_args__ = (Index('idx_game_subjects_active', 'is_active'),)


class GameTopic(Base):
    """Topics within subjects: Tense, Articles, Prepositions, Voice"""
    __tablename__ = 'game_topics'
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey('game_subjects.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(255))
    order_index = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    subject = relationship('GameSubject', back_populates='topics')
    levels = relationship('GameLevel', back_populates='topic', cascade='all, delete-orphan')
    topic_progress = relationship('TopicProgress', back_populates='topic', cascade='all, delete-orphan')
    weak_areas = relationship('WeakArea', back_populates='topic', cascade='all, delete-orphan')
    
    __table_args__ = (
        UniqueConstraint('subject_id', 'name', name='unique_subject_topic'),
        Index('idx_game_topics_subject', 'subject_id'),
        Index('idx_game_topics_active', 'is_active'),
    )


class GameLevel(Base):
    """Levels per topic: Level 1, 2, 3, Boss Level"""
    __tablename__ = 'game_levels'
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey('game_topics.id', ondelete='CASCADE'), nullable=False)
    level_number = Column(Integer, nullable=False)
    title = Column(String(120), nullable=False)
    level_type = Column(Enum(LevelTypeEnum), default=LevelTypeEnum.NORMAL)
    
    # Admin Settings
    difficulty = Column(Enum(DifficultyEnum), nullable=False)
    pass_score = Column(Integer, default=70)  # Percentage needed to pass
    time_limit_seconds = Column(Integer, default=300)
    question_count = Column(Integer, default=10)
    question_types = Column(JSON, default=lambda: ["mcq"])
    
    # Rewards
    xp_reward = Column(Integer, default=100)
    boss_xp_multiplier = Column(Float, default=2.0)
    
    # AI Configuration
    ai_prompt_template = Column(Text)
    ai_generation_rules = Column(JSON)
    ai_model_used = Column(String(50), default="gpt-4")
    
    # Status
    order_index = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    topic = relationship('GameTopic', back_populates='levels')
    questions = relationship('GameQuestion', back_populates='level', cascade='all, delete-orphan')
    fallback_questions = relationship('FallbackQuestion', back_populates='level', cascade='all, delete-orphan')
    level_progress = relationship('LevelProgress', back_populates='level', cascade='all, delete-orphan')
    attempts = relationship('LevelAttempt', back_populates='level', cascade='all, delete-orphan')
    weak_areas = relationship('WeakArea', back_populates='level', cascade='all, delete-orphan')
    
    __table_args__ = (
        UniqueConstraint('topic_id', 'level_number', name='unique_topic_level'),
        Index('idx_game_levels_topic', 'topic_id'),
        Index('idx_game_levels_type', 'level_type'),
        Index('idx_game_levels_active', 'is_active'),
    )


class LevelLock(Base):
    """Prerequisites for unlocking levels"""
    __tablename__ = 'game_level_locks'
    
    id = Column(Integer, primary_key=True, index=True)
    level_id = Column(Integer, ForeignKey('game_levels.id', ondelete='CASCADE'), nullable=False, index=True)
    prerequisite_level_id = Column(Integer, ForeignKey('game_levels.id', ondelete='CASCADE'), index=True)
    required_score = Column(Integer, default=70)  # Min score to unlock
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('level_id', 'prerequisite_level_id', name='unique_level_prerequisite'),
        Index('idx_game_level_locks_level', 'level_id'),
        Index('idx_game_level_locks_prerequisite', 'prerequisite_level_id'),
    )


# ═══════════════════════════════════════════════════════════════════════════
# QUESTION BANK TABLES
# ═══════════════════════════════════════════════════════════════════════════

class GameQuestion(Base):
    """AI-generated or verified questions"""
    __tablename__ = 'game_questions'
    
    id = Column(Integer, primary_key=True, index=True)
    level_id = Column(Integer, ForeignKey('game_levels.id', ondelete='CASCADE'), nullable=False)
    question_type = Column(Enum(QuestionTypeEnum), nullable=False)
    
    # Content
    question_text = Column(Text, nullable=False)
    question_media = Column(String(255))  # URL to image/audio
    options = Column(JSON)  # For MCQ/match type
    correct_answer = Column(JSON, nullable=False)  # Flexible format
    explanation = Column(Text)
    difficulty_score = Column(Float, default=0.0)
    
    # Source
    source = Column(Enum(QuestionSourceEnum), default=QuestionSourceEnum.AI_GENERATED)
    ai_model_used = Column(String(50))
    ai_generation_prompt = Column(Text)
    
    # Quality
    is_verified = Column(Boolean, default=False)
    verification_notes = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Analytics
    attempts_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    level = relationship('GameLevel', back_populates='questions')
    responses = relationship('QuestionResponse', back_populates='question', cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('idx_game_questions_level', 'level_id'),
        Index('idx_game_questions_type', 'question_type'),
        Index('idx_game_questions_source', 'source'),
        Index('idx_game_questions_active', 'is_active'),
        Index('idx_game_questions_verified', 'is_verified'),
    )


class FallbackQuestion(Base):
    """Admin manual questions for consistency"""
    __tablename__ = 'game_fallback_questions'
    
    id = Column(Integer, primary_key=True, index=True)
    level_id = Column(Integer, ForeignKey('game_levels.id', ondelete='CASCADE'), nullable=False)
    question_type = Column(Enum(QuestionTypeEnum), nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSON)
    correct_answer = Column(JSON, nullable=False)
    explanation = Column(Text)
    priority = Column(Integer, default=0)  # Higher priority = used first
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    level = relationship('GameLevel', back_populates='fallback_questions')
    
    __table_args__ = (
        Index('idx_game_fallback_questions_level', 'level_id'),
        Index('idx_game_fallback_questions_priority', 'priority'),
    )


class QuestionCache(Base):
    """Cache for generated questions"""
    __tablename__ = 'game_question_cache'
    
    id = Column(Integer, primary_key=True, index=True)
    level_id = Column(Integer, ForeignKey('game_levels.id', ondelete='CASCADE'), nullable=False)
    cached_questions = Column(JSON, nullable=False)
    generated_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime)
    generation_metadata = Column(JSON)
    
    __table_args__ = (
        Index('idx_game_question_cache_level', 'level_id'),
        Index('idx_game_question_cache_expires', 'expires_at'),
    )


# ═══════════════════════════════════════════════════════════════════════════
# USER PROGRESS & GAME STATE TABLES
# ═══════════════════════════════════════════════════════════════════════════

class GameUserProgress(Base):
    """User's overall game progress and profile"""
    __tablename__ = 'game_user_progress'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    
    # Overall Stats
    total_xp = Column(Integer, default=0)
    current_tier = Column(Enum(UserTierEnum), default=UserTierEnum.BRONZE)
    current_streak = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)
    
    # Hearts
    total_hearts = Column(Integer, default=5)
    current_hearts = Column(Integer, default=5)
    last_heart_refill = Column(DateTime)
    
    # Status
    daily_mission_completed = Column(Boolean, default=False)
    last_active_at = Column(DateTime)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_game_user_progress_user', 'user_id'),
        Index('idx_game_user_progress_tier', 'current_tier'),
    )


class SubjectProgress(Base):
    """User's progress per subject"""
    __tablename__ = 'game_subject_progress'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    subject_id = Column(Integer, ForeignKey('game_subjects.id', ondelete='CASCADE'), nullable=False)
    
    xp_earned = Column(Integer, default=0)
    last_attempted_at = Column(DateTime)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('user_id', 'subject_id', name='unique_user_subject_game'),
        Index('idx_game_subject_progress_user', 'user_id'),
        Index('idx_game_subject_progress_subject', 'subject_id'),
    )


class TopicProgress(Base):
    """User's progress per topic"""
    __tablename__ = 'game_topic_progress'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    topic_id = Column(Integer, ForeignKey('game_topics.id', ondelete='CASCADE'), nullable=False)
    
    xp_earned = Column(Integer, default=0)
    mastery_score = Column(Float, default=0.0)  # 0-100
    weakness_detected = Column(Boolean, default=False)
    weakness_triggered_count = Column(Integer, default=0)
    last_weak_attempt = Column(DateTime)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    topic = relationship('GameTopic', back_populates='topic_progress')
    
    __table_args__ = (
        UniqueConstraint('user_id', 'topic_id', name='unique_user_topic_game'),
        Index('idx_game_topic_progress_user', 'user_id'),
        Index('idx_game_topic_progress_topic', 'topic_id'),
        Index('idx_game_topic_progress_weakness', 'weakness_detected'),
    )


class LevelProgress(Base):
    """User's progress per level"""
    __tablename__ = 'game_level_progress'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    level_id = Column(Integer, ForeignKey('game_levels.id', ondelete='CASCADE'), nullable=False)
    
    # Status
    is_unlocked = Column(Boolean, default=False)
    is_passed = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)
    unlock_date = Column(DateTime)
    completion_date = Column(DateTime)
    
    # Performance
    attempts = Column(Integer, default=0)
    best_score = Column(Integer, default=0)
    best_stars = Column(Integer, default=0)  # 1, 2, or 3
    
    # Current state
    current_hearts = Column(Integer)
    current_xp = Column(Integer, default=0)
    mistakes_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    level = relationship('GameLevel', back_populates='level_progress')
    
    __table_args__ = (
        UniqueConstraint('user_id', 'level_id', name='unique_user_level_game'),
        Index('idx_game_level_progress_user', 'user_id'),
        Index('idx_game_level_progress_level', 'level_id'),
        Index('idx_game_level_progress_unlocked', 'is_unlocked'),
        Index('idx_game_level_progress_passed', 'is_passed'),
    )


class LevelAttempt(Base):
    """Each level play session"""
    __tablename__ = 'game_level_attempts'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    level_id = Column(Integer, ForeignKey('game_levels.id', ondelete='CASCADE'), nullable=False)
    
    # Timing
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)
    
    # Performance
    questions_attempted = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)
    final_score = Column(Integer, default=0)  # Percentage
    stars_earned = Column(Integer, default=0)
    
    # Hearts & Streaks
    hearts_used = Column(Integer, default=0)
    combo_count = Column(Integer, default=0)
    streak_broken = Column(Boolean, default=False)
    
    # XP Breakdown
    base_xp = Column(Integer, default=0)
    combo_bonus_xp = Column(Integer, default=0)
    streak_bonus_xp = Column(Integer, default=0)
    perfect_bonus_xp = Column(Integer, default=0)
    confidence_bonus_xp = Column(Integer, default=0)
    total_xp_earned = Column(Integer, default=0)
    
    # Confidence Data
    confident_answers = Column(Integer, default=0)
    unsure_answers = Column(Integer, default=0)
    
    # Questions used
    question_ids = Column(JSON)  # Array of question IDs
    
    # Status
    is_passed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    level = relationship('GameLevel', back_populates='attempts')
    responses = relationship('QuestionResponse', back_populates='attempt', cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('idx_game_level_attempts_user', 'user_id'),
        Index('idx_game_level_attempts_level', 'level_id'),
        Index('idx_game_level_attempts_passed', 'is_passed'),
        Index('idx_game_level_attempts_created', 'created_at'),
    )


class QuestionResponse(Base):
    """User's response to a question"""
    __tablename__ = 'game_question_responses'
    
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey('game_level_attempts.id', ondelete='CASCADE'), nullable=False)
    question_id = Column(Integer, ForeignKey('game_questions.id', ondelete='CASCADE'), nullable=False)
    
    # Response
    user_answer = Column(JSON)
    is_correct = Column(Boolean)
    time_taken_seconds = Column(Integer)
    confidence_level = Column(Enum(ConfidenceLevelEnum))
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    attempt = relationship('LevelAttempt', back_populates='responses')
    question = relationship('GameQuestion', back_populates='responses')
    
    __table_args__ = (
        Index('idx_game_question_responses_attempt', 'attempt_id'),
        Index('idx_game_question_responses_question', 'question_id'),
        Index('idx_game_question_responses_correct', 'is_correct'),
    )


# ═══════════════════════════════════════════════════════════════════════════
# WEAK AREAS & SPACED REPETITION
# ═══════════════════════════════════════════════════════════════════════════

class WeakArea(Base):
    """Detected weak areas for users"""
    __tablename__ = 'game_weak_areas'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    topic_id = Column(Integer, ForeignKey('game_topics.id', ondelete='CASCADE'), nullable=False)
    level_id = Column(Integer, ForeignKey('game_levels.id', ondelete='CASCADE'))
    
    # Detection
    failure_count = Column(Integer, default=0)
    last_failure_at = Column(DateTime)
    detection_threshold = Column(Integer, default=3)
    is_active = Column(Boolean, default=True)
    
    # Remediation
    mini_practice_session_id = Column(Integer, ForeignKey('game_level_attempts.id'))
    next_review_date = Column(DateTime)
    review_interval_days = Column(Integer, default=1)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    topic = relationship('GameTopic', back_populates='weak_areas')
    level = relationship('GameLevel', back_populates='weak_areas')
    
    __table_args__ = (
        UniqueConstraint('user_id', 'topic_id', name='unique_user_weak_topic'),
        Index('idx_game_weak_areas_user', 'user_id'),
        Index('idx_game_weak_areas_topic', 'topic_id'),
        Index('idx_game_weak_areas_active', 'is_active'),
        Index('idx_game_weak_areas_review_date', 'next_review_date'),
    )


class SpacedRepetitionQueue(Base):
    """Spaced repetition scheduler"""
    __tablename__ = 'game_spaced_repetition_queue'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    topic_id = Column(Integer, ForeignKey('game_topics.id', ondelete='CASCADE'), nullable=False)
    
    # Scheduling (SM-2 algorithm)
    due_date = Column(DateTime, nullable=False)
    review_count = Column(Integer, default=0)
    interval_days = Column(Integer, default=1)
    ease_factor = Column(Float, default=2.5)
    quality = Column(Integer, default=0)  # 0-5 rating
    
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_game_spaced_rep_user', 'user_id'),
        Index('idx_game_spaced_rep_due_date', 'due_date'),
        Index('idx_game_spaced_rep_completed', 'is_completed'),
    )


# ═══════════════════════════════════════════════════════════════════════════
# GAMIFICATION TABLES
# ═══════════════════════════════════════════════════════════════════════════

class DailyMission(Base):
    """Daily missions configuration"""
    __tablename__ = 'game_daily_missions'
    
    id = Column(Integer, primary_key=True, index=True)
    mission_date = Column(DateTime, nullable=False, unique=True)
    
    # Mission 1
    mission_1_description = Column(String(255))
    mission_1_target = Column(Integer)
    mission_1_reward_xp = Column(Integer, default=50)
    
    # Mission 2
    mission_2_description = Column(String(255))
    mission_2_target = Column(Integer)
    mission_2_reward_xp = Column(Integer, default=50)
    
    # Boss
    boss_challenge_id = Column(Integer, ForeignKey('game_levels.id'))
    boss_reward_xp = Column(Integer, default=100)
    
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (Index('idx_game_daily_missions_date', 'mission_date'),)


class UserDailyMission(Base):
    """User's daily mission progress"""
    __tablename__ = 'game_user_daily_missions'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    daily_mission_id = Column(Integer, ForeignKey('game_daily_missions.id', ondelete='CASCADE'), nullable=False)
    
    mission_1_progress = Column(Integer, default=0)
    mission_1_completed = Column(Boolean, default=False)
    
    mission_2_progress = Column(Integer, default=0)
    mission_2_completed = Column(Boolean, default=False)
    
    boss_completed = Column(Boolean, default=False)
    all_completed = Column(Boolean, default=False)
    completion_reward_claimed = Column(Boolean, default=False)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('user_id', 'daily_mission_id', name='unique_user_daily_mission_game'),
        Index('idx_game_user_daily_missions_user', 'user_id'),
        Index('idx_game_user_daily_missions_completed', 'all_completed'),
    )


class GameBadge(Base):
    """Game badges and achievements"""
    __tablename__ = 'game_badges'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    icon = Column(String(255))
    trigger_condition = Column(String(255))  # 'first_perfect', 'streak_7'
    reward_xp = Column(Integer, default=0)
    tier = Column(String(20), default='normal')  # normal, rare, epic, legendary
    created_at = Column(DateTime, server_default=func.now())
    
    user_badges = relationship('UserGameBadge', back_populates='badge')
    
    __table_args__ = (Index('idx_game_badges_tier', 'tier'),)


class UserGameBadge(Base):
    """User's earned badges"""
    __tablename__ = 'game_user_badges'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    badge_id = Column(Integer, ForeignKey('game_badges.id', ondelete='CASCADE'), nullable=False)
    
    earned_at = Column(DateTime, server_default=func.now())
    
    badge = relationship('GameBadge', back_populates='user_badges')
    
    __table_args__ = (
        UniqueConstraint('user_id', 'badge_id', name='unique_user_badge_game'),
        Index('idx_game_user_badges_user', 'user_id'),
    )


class RewardChest(Base):
    """Reward chests (unlock after 3 levels)"""
    __tablename__ = 'game_reward_chests'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    unlocked_date = Column(DateTime)
    reward_type = Column(String(50))  # 'xp', 'hearts', 'badge', 'streak_shield'
    reward_value = Column(Integer)
    is_claimed = Column(Boolean, default=False)
    claimed_at = Column(DateTime)
    
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        Index('idx_game_reward_chests_user', 'user_id'),
        Index('idx_game_reward_chests_claimed', 'is_claimed'),
    )


class Leaderboard(Base):
    """Leaderboard rankings"""
    __tablename__ = 'game_leaderboard'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    rank = Column(Integer)
    total_xp = Column(Integer)
    streak = Column(Integer)
    tier = Column(Enum(UserTierEnum))
    
    period = Column(String(20), default='weekly')  # weekly, monthly, all-time
    calculated_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('user_id', 'period', name='unique_user_period_game'),
        Index('idx_game_leaderboard_period', 'period'),
        Index('idx_game_leaderboard_rank', 'rank'),
    )


class FriendChallenge(Base):
    """Friend challenges"""
    __tablename__ = 'game_friend_challenges'
    
    id = Column(Integer, primary_key=True, index=True)
    challenger_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    opponent_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    topic_id = Column(Integer, ForeignKey('game_topics.id', ondelete='CASCADE'), nullable=False)
    
    challenger_score = Column(Integer, default=0)
    opponent_score = Column(Integer, default=0)
    
    status = Column(Enum(ChallengeStatusEnum), default=ChallengeStatusEnum.PENDING)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    
    winner_id = Column(Integer, ForeignKey('users.id'))
    
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        Index('idx_game_friend_challenges_challenger', 'challenger_id'),
        Index('idx_game_friend_challenges_opponent', 'opponent_id'),
        Index('idx_game_friend_challenges_status', 'status'),
    )


# ═══════════════════════════════════════════════════════════════════════════
# PLACEMENT TEST TABLES
# ═══════════════════════════════════════════════════════════════════════════

class PlacementTest(Base):
    """Placement test configuration"""
    __tablename__ = 'game_placement_tests'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    question_count = Column(Integer, default=15)
    time_limit_seconds = Column(Integer, default=600)
    question_types = Column(JSON)
    score_ranges = Column(JSON)  # Scoring matrix
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (Index('idx_game_placement_tests_active', 'is_active'),)


class PlacementTestResult(Base):
    """User's placement test result"""
    __tablename__ = 'game_placement_test_results'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    placement_test_id = Column(Integer, ForeignKey('game_placement_tests.id', ondelete='CASCADE'), nullable=False)
    
    score = Column(Integer)
    recommended_subject_id = Column(Integer, ForeignKey('game_subjects.id'))
    recommended_topic_id = Column(Integer, ForeignKey('game_topics.id'))
    recommended_level = Column(Integer)
    
    completed_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('user_id', 'placement_test_id', name='unique_user_placement_test_game'),
        Index('idx_game_placement_results_user', 'user_id'),
    )
