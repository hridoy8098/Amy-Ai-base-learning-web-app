from sqlalchemy import (
    Column, Integer, String, Text, Boolean,
    DateTime, Float, ForeignKey, JSON, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
import enum


class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(100), nullable=False)
    email         = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    avatar        = Column(String(500), nullable=True)
    bio           = Column(Text, nullable=True)
    role          = Column(String(20), default="user")
    is_active     = Column(Boolean, default=True)
    is_verified   = Column(Boolean, default=False)
    subscription_plan    = Column(String(20), default="free")
    subscription_expires = Column(DateTime, nullable=True)
    xp_points     = Column(Integer, default=0)
    streak_days   = Column(Integer, default=0)
    last_active   = Column(DateTime, nullable=True)
    level         = Column(Integer, default=1)
    amy_messages_today   = Column(Integer, default=0)
    amy_voice_today      = Column(Integer, default=0)
    quiz_generated_today = Column(Integer, default=0)
    last_usage_reset     = Column(DateTime, nullable=True)
    referral_code = Column(String(20), unique=True, nullable=True)
    referred_by   = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at    = Column(DateTime, server_default=func.now())
    updated_at    = Column(DateTime, server_default=func.now(), onupdate=func.now())

    enrollments     = relationship("Enrollment", back_populates="user")
    payments        = relationship("Payment", back_populates="user")
    quiz_results    = relationship("QuizResult", back_populates="user")
    amy_sessions    = relationship("AmySession", back_populates="user")
    amy_messages    = relationship("AmyMessage", back_populates="user")
    notes           = relationship("Note", back_populates="user")
    bookmarks       = relationship("Bookmark", back_populates="user")
    badges          = relationship("UserBadge", back_populates="user")
    certificates    = relationship("Certificate", back_populates="user")
    lesson_progress = relationship("LessonProgress", back_populates="user")
    reviews         = relationship("CourseReview", back_populates="user")
    notifications   = relationship("Notification", back_populates="user")


class Category(Base):
    __tablename__ = "categories"
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), nullable=False)
    slug        = Column(String(120), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon        = Column(String(10), nullable=True)
    color       = Column(String(20), nullable=True)
    is_active   = Column(Boolean, default=True)
    sort_order  = Column(Integer, default=0)
    created_at  = Column(DateTime, server_default=func.now())
    courses     = relationship("Course", back_populates="category")


class Course(Base):
    __tablename__ = "courses"
    id             = Column(Integer, primary_key=True, index=True)
    title          = Column(String(200), nullable=False)
    slug           = Column(String(220), unique=True, nullable=False)
    description    = Column(Text, nullable=True)
    short_desc     = Column(String(500), nullable=True)
    thumbnail      = Column(String(500), nullable=True)
    trailer_video  = Column(String(500), nullable=True)
    level          = Column(String(20), default="beginner")
    language       = Column(String(10), default="en")
    status         = Column(String(20), default="draft")
    is_free        = Column(Boolean, default=False)
    price          = Column(Float, default=0.0)
    discount_price = Column(Float, nullable=True)
    total_lessons  = Column(Integer, default=0)
    total_duration = Column(Integer, default=0)
    enrolled_count = Column(Integer, default=0)
    rating_avg     = Column(Float, default=0.0)
    rating_count   = Column(Integer, default=0)
    what_you_learn = Column(JSON, nullable=True)
    requirements   = Column(JSON, nullable=True)
    tags           = Column(JSON, nullable=True)
    category_id    = Column(Integer, ForeignKey("categories.id"), nullable=True)
    instructor_id  = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at     = Column(DateTime, server_default=func.now())
    updated_at     = Column(DateTime, server_default=func.now(), onupdate=func.now())

    category     = relationship("Category", back_populates="courses")
    instructor   = relationship("User")
    lessons      = relationship("Lesson", back_populates="course", order_by="Lesson.sort_order")
    enrollments  = relationship("Enrollment", back_populates="course")
    reviews      = relationship("CourseReview", back_populates="course")
    certificates = relationship("Certificate", back_populates="course")


class Lesson(Base):
    __tablename__ = "lessons"
    id           = Column(Integer, primary_key=True, index=True)
    title        = Column(String(200), nullable=False)
    description  = Column(Text, nullable=True)
    content      = Column(Text, nullable=True)
    lesson_type  = Column(String(20), default="text")
    video_url    = Column(String(500), nullable=True)
    video_type   = Column(String(20), nullable=True)
    file_url     = Column(String(500), nullable=True)
    duration     = Column(Integer, default=0)
    sort_order   = Column(Integer, default=0)
    is_free      = Column(Boolean, default=False)
    is_published = Column(Boolean, default=True)
    course_id    = Column(Integer, ForeignKey("courses.id"), nullable=False)
    created_at   = Column(DateTime, server_default=func.now())
    updated_at   = Column(DateTime, server_default=func.now(), onupdate=func.now())

    course    = relationship("Course", back_populates="lessons")
    progress  = relationship("LessonProgress", back_populates="lesson")
    notes     = relationship("Note", back_populates="lesson")
    bookmarks = relationship("Bookmark", back_populates="lesson")


class Enrollment(Base):
    __tablename__ = "enrollments"
    id             = Column(Integer, primary_key=True, index=True)
    user_id        = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id      = Column(Integer, ForeignKey("courses.id"), nullable=False)
    progress       = Column(Float, default=0.0)
    completed      = Column(Boolean, default=False)
    last_lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=True)
    enrolled_at    = Column(DateTime, server_default=func.now())
    completed_at   = Column(DateTime, nullable=True)

    user   = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id     = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    completed     = Column(Boolean, default=False)
    watch_seconds = Column(Integer, default=0)
    completed_at  = Column(DateTime, nullable=True)
    created_at    = Column(DateTime, server_default=func.now())

    user   = relationship("User", back_populates="lesson_progress")
    lesson = relationship("Lesson", back_populates="progress")


class Payment(Base):
    __tablename__ = "payments"
    id             = Column(Integer, primary_key=True, index=True)
    user_id        = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id      = Column(Integer, ForeignKey("courses.id"), nullable=True)
    amount         = Column(Float, nullable=False)
    currency       = Column(String(10), default="BDT")
    method         = Column(String(20), nullable=False)
    status         = Column(String(20), default="pending")
    transaction_id = Column(String(200), nullable=True)
    payment_type   = Column(String(30), default="course")
    plan           = Column(String(20), nullable=True)
    notes          = Column(Text, nullable=True)
    created_at     = Column(DateTime, server_default=func.now())
    updated_at     = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user   = relationship("User", back_populates="payments")
    course = relationship("Course")


class QuizResult(Base):
    __tablename__ = "quiz_results"
    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic       = Column(String(200), nullable=False)
    subject     = Column(String(200), nullable=True)
    difficulty  = Column(String(20), default="intermediate")
    language    = Column(String(10), default="en")
    total_q     = Column(Integer, default=0)
    correct     = Column(Integer, default=0)
    score       = Column(Float, default=0.0)
    xp_earned   = Column(Integer, default=0)
    questions   = Column(JSON, nullable=True)
    created_at  = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="quiz_results")


class AmySession(Base):
    __tablename__ = "amy_sessions"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    mode       = Column(String(20), default="general")
    language   = Column(String(10), default="en")
    title      = Column(String(200), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user     = relationship("User", back_populates="amy_sessions")
    messages = relationship("AmyMessage", back_populates="session", order_by="AmyMessage.id")


class AmyMessage(Base):
    __tablename__ = "amy_messages"
    id         = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("amy_sessions.id"), nullable=False)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    role       = Column(String(20), nullable=False)
    content    = Column(Text, nullable=False)
    mood       = Column(String(30), nullable=True)
    provider   = Column(String(50), nullable=True)
    xp_earned  = Column(Integer, default=0)
    is_voice   = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    session = relationship("AmySession", back_populates="messages")
    user    = relationship("User", back_populates="amy_messages")


class Note(Base):
    __tablename__ = "notes"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id  = Column(Integer, ForeignKey("lessons.id"), nullable=True)
    title      = Column(String(200), nullable=True)
    content    = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user   = relationship("User", back_populates="notes")
    lesson = relationship("Lesson", back_populates="notes")


class Bookmark(Base):
    __tablename__ = "bookmarks"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id  = Column(Integer, ForeignKey("lessons.id"), nullable=True)
    course_id  = Column(Integer, ForeignKey("courses.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user   = relationship("User", back_populates="bookmarks")
    lesson = relationship("Lesson", back_populates="bookmarks")


class Badge(Base):
    __tablename__ = "badges"
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon        = Column(String(10), nullable=True)
    condition   = Column(String(50), nullable=False)
    xp_reward   = Column(Integer, default=0)
    created_at  = Column(DateTime, server_default=func.now())

    user_badges = relationship("UserBadge", back_populates="badge")


class UserBadge(Base):
    __tablename__ = "user_badges"
    id        = Column(Integer, primary_key=True, index=True)
    user_id   = Column(Integer, ForeignKey("users.id"), nullable=False)
    badge_id  = Column(Integer, ForeignKey("badges.id"), nullable=False)
    earned_at = Column(DateTime, server_default=func.now())

    user  = relationship("User", back_populates="badges")
    badge = relationship("Badge", back_populates="user_badges")


class Certificate(Base):
    __tablename__ = "certificates"
    id        = Column(Integer, primary_key=True, index=True)
    user_id   = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    cert_code = Column(String(50), unique=True, nullable=False)
    issued_at = Column(DateTime, server_default=func.now())
    file_path = Column(String(500), nullable=True)

    user   = relationship("User", back_populates="certificates")
    course = relationship("Course", back_populates="certificates")


class CourseReview(Base):
    __tablename__ = "course_reviews"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id  = Column(Integer, ForeignKey("courses.id"), nullable=False)
    rating     = Column(Integer, nullable=False)
    comment    = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user   = relationship("User", back_populates="reviews")
    course = relationship("Course", back_populates="reviews")


class Notification(Base):
    __tablename__ = "notifications"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    title      = Column(String(200), nullable=False)
    message    = Column(Text, nullable=False)
    type       = Column(String(30), default="info")
    is_read    = Column(Boolean, default=False)
    link       = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="notifications")


class SavedVocab(Base):
    __tablename__ = "saved_vocab"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    word       = Column(String(200), nullable=False)
    definition = Column(Text, nullable=True)
    example    = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class Coupon(Base):
    __tablename__ = "coupons"
    id           = Column(Integer, primary_key=True, index=True)
    code         = Column(String(50), unique=True, nullable=False)
    discount_pct = Column(Float, default=0.0)
    discount_amt = Column(Float, default=0.0)
    max_uses     = Column(Integer, default=100)
    used_count   = Column(Integer, default=0)
    is_active    = Column(Boolean, default=True)
    expires_at   = Column(DateTime, nullable=True)
    created_at   = Column(DateTime, server_default=func.now())


# ── New Feature Models ─────────────────────────────────────────────

class FluencyRecord(Base):
    __tablename__ = "fluency_records"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    score      = Column(Float, nullable=False)
    mode       = Column(String(20), default="english")
    session_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class UserMemory(Base):
    __tablename__ = "user_memories"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    category   = Column(String(50), nullable=False)
    key        = Column(String(100), nullable=False)
    value      = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class GrammarMistake(Base):
    __tablename__ = "grammar_mistakes"
    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    error_type  = Column(String(100), nullable=False)
    original    = Column(Text, nullable=False)
    correction  = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    count       = Column(Integer, default=1)
    created_at  = Column(DateTime, server_default=func.now())
    updated_at  = Column(DateTime, server_default=func.now(), onupdate=func.now())

class UserGoal(Base):
    __tablename__ = "user_goals"
    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_type    = Column(String(50), nullable=False)
    target_score = Column(Float, nullable=True)
    deadline     = Column(DateTime, nullable=True)
    study_plan   = Column(Text, nullable=True)
    is_active    = Column(Boolean, default=True)
    progress_pct = Column(Float, default=0.0)
    created_at   = Column(DateTime, server_default=func.now())
    updated_at   = Column(DateTime, server_default=func.now(), onupdate=func.now())

class SmartReminder(Base):
    __tablename__ = "smart_reminders"
    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id"), nullable=False)
    reminder_time = Column(String(10), nullable=False)
    days          = Column(String(50), default="mon,tue,wed,thu,fri,sat,sun")
    message_type  = Column(String(30), default="daily_practice")
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime, server_default=func.now())

class MicroCertificate(Base):
    __tablename__ = "micro_certificates"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_id   = Column(String(50), nullable=False)
    skill_name = Column(String(100), nullable=False)
    cert_code  = Column(String(50), unique=True, nullable=False)
    issued_at  = Column(DateTime, server_default=func.now())
    share_url  = Column(String(300), nullable=True)


class PlacementSubject(Base):
    __tablename__ = "placement_subjects"
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon        = Column(String(20), nullable=True)
    sort_order  = Column(Integer, default=0)
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime, server_default=func.now())


class PlacementTopic(Base):
    __tablename__ = "placement_topics"
    id          = Column(Integer, primary_key=True, index=True)
    subject_id  = Column(Integer, ForeignKey("placement_subjects.id"), nullable=False)
    name        = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    ai_prompt   = Column(Text, nullable=True)
    sort_order  = Column(Integer, default=0)
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime, server_default=func.now())


class PlacementLevel(Base):
    __tablename__ = "placement_levels"
    id             = Column(Integer, primary_key=True, index=True)
    topic_id       = Column(Integer, ForeignKey("placement_topics.id"), nullable=False)
    title          = Column(String(120), nullable=False)
    level_no       = Column(Integer, default=1)
    difficulty     = Column(String(30), default="beginner")
    question_count = Column(Integer, default=5)
    time_limit     = Column(Integer, default=60)
    hearts         = Column(Integer, default=3)
    pass_score     = Column(Float, default=60.0)
    reward_xp      = Column(Integer, default=20)
    question_types = Column(JSON, nullable=True)
    ai_prompt      = Column(Text, nullable=True)
    is_boss        = Column(Boolean, default=False)
    is_active      = Column(Boolean, default=True)
    created_at     = Column(DateTime, server_default=func.now())


class PlacementQuestion(Base):
    __tablename__ = "placement_questions"
    id            = Column(Integer, primary_key=True, index=True)
    level_id       = Column(Integer, ForeignKey("placement_levels.id"), nullable=False)
    question_type  = Column(String(30), default="mcq")
    prompt         = Column(Text, nullable=False)
    options        = Column(JSON, nullable=True)
    correct_index  = Column(Integer, default=0)
    explanation    = Column(Text, nullable=True)
    is_active      = Column(Boolean, default=True)
    created_at     = Column(DateTime, server_default=func.now())


class UserPlacementProgress(Base):
    __tablename__ = "user_placement_progress"
    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id"), nullable=False)
    level_id      = Column(Integer, ForeignKey("placement_levels.id"), nullable=False)
    attempts_count = Column(Integer, default=0)
    best_score    = Column(Float, default=0.0)
    stars         = Column(Integer, default=0)
    completed     = Column(Boolean, default=False)
    last_played_at = Column(DateTime, nullable=True)
    created_at    = Column(DateTime, server_default=func.now())
    updated_at    = Column(DateTime, server_default=func.now(), onupdate=func.now())


class PlacementAttempt(Base):
    __tablename__ = "placement_attempts"
    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    level_id     = Column(Integer, ForeignKey("placement_levels.id"), nullable=False)
    questions    = Column(JSON, nullable=False)
    answers      = Column(JSON, nullable=True)
    score        = Column(Float, default=0.0)
    stars        = Column(Integer, default=0)
    hearts_left  = Column(Integer, default=3)
    xp_earned    = Column(Integer, default=0)
    passed       = Column(Boolean, default=False)
    created_at   = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
