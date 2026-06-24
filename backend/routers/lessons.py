from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from core.database import get_db
from core.security import get_current_user, get_current_admin
from models.models import Lesson, Course, LessonProgress, Enrollment
from datetime import datetime

router = APIRouter()

class LessonCreate(BaseModel):
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    lesson_type: str = "text"
    video_url: Optional[str] = None
    video_type: Optional[str] = None
    file_url: Optional[str] = None
    duration: int = 0
    sort_order: int = 0
    is_free: bool = False
    is_published: bool = True
    course_id: int

class LessonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    lesson_type: Optional[str] = None
    video_url: Optional[str] = None
    video_type: Optional[str] = None
    file_url: Optional[str] = None
    duration: Optional[int] = None
    sort_order: Optional[int] = None
    is_free: Optional[bool] = None
    is_published: Optional[bool] = None

class VideoProgress(BaseModel):
    watch_seconds: int

def _lesson(l):
    return {
        "id": l.id,
        "title": l.title,
        "description": l.description,
        "content": l.content,
        "lesson_type": l.lesson_type,
        "video_url": l.video_url,
        "video_type": l.video_type,
        "file_url": l.file_url,
        "duration": l.duration,
        "sort_order": l.sort_order,
        "is_free": l.is_free,
        "is_published": l.is_published,
        "course_id": l.course_id,
        "created_at": l.created_at.isoformat() if l.created_at else None
    }

def _sync_course(course_id, db):
    c = db.query(Course).filter(Course.id == course_id).first()
    if c:
        ls = db.query(Lesson).filter(
            Lesson.course_id == course_id,
            Lesson.is_published == True
        ).all()
        c.total_lessons = len(ls)
        c.total_duration = sum(l.duration for l in ls)
        db.commit()

# ─────────────────────────────────────────────
# PUBLIC: lesson list with locked flag
# Called by frontend when rendering course detail & lesson page
# ─────────────────────────────────────────────
@router.get("/public/course/{course_id}")
def get_public_lessons(
    course_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Returns lessons for a course with 'locked' flag.
    - Free lessons: always unlocked
    - Paid lessons: unlocked only if user is enrolled
    """
    lessons = db.query(Lesson).filter(
        Lesson.course_id == course_id,
        Lesson.is_published == True
    ).order_by(Lesson.sort_order).all()

    # Check if user is enrolled
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == user.id,
        Enrollment.course_id == course_id
    ).first()
    is_enrolled = enrollment is not None

    result = []
    for l in lessons:
        data = _lesson(l)
        data["locked"] = not (is_enrolled or l.is_free)
        data["completed"] = False  # will be filled by progress endpoint
        result.append(data)

    return result


# ─────────────────────────────────────────────
# PUBLIC: single lesson detail (enrolled or free only)
# ─────────────────────────────────────────────
@router.get("/detail/{lesson_id}")
def get_lesson_detail(
    lesson_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Returns full lesson content.
    Blocks if lesson is paid and user is not enrolled.
    """
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id,
        Lesson.is_published == True
    ).first()
    if not lesson:
        raise HTTPException(404, "Lesson not found")

    # Check access
    if not lesson.is_free:
        enrollment = db.query(Enrollment).filter(
            Enrollment.user_id == user.id,
            Enrollment.course_id == lesson.course_id
        ).first()
        if not enrollment:
            raise HTTPException(403, "Enroll to access this lesson")

    data = _lesson(lesson)

    # Add progress info
    progress = db.query(LessonProgress).filter(
        LessonProgress.user_id == user.id,
        LessonProgress.lesson_id == lesson_id
    ).first()
    data["completed"] = progress.completed if progress else False
    data["watch_seconds"] = progress.watch_seconds if progress else 0

    return data


# ─────────────────────────────────────────────
# ADMIN: full lesson list (all, including unpublished)
# ─────────────────────────────────────────────
@router.get("/course/{course_id}")
def get_lessons(
    course_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    return [
        _lesson(l) for l in db.query(Lesson)
        .filter(Lesson.course_id == course_id)
        .order_by(Lesson.sort_order).all()
    ]


@router.post("")
def create_lesson(
    req: LessonCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    if not db.query(Course).filter(Course.id == req.course_id).first():
        raise HTTPException(404, "Course not found")
    l = Lesson(**req.dict())
    db.add(l)
    db.commit()
    db.refresh(l)
    _sync_course(req.course_id, db)
    return _lesson(l)


@router.put("/{lesson_id}")
def update_lesson(
    lesson_id: int,
    req: LessonUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    l = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not l:
        raise HTTPException(404, "Not found")
    for k, v in req.dict(exclude_unset=True).items():
        setattr(l, k, v)
    db.commit()
    db.refresh(l)
    _sync_course(l.course_id, db)
    return _lesson(l)


@router.delete("/{lesson_id}")
def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    l = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not l:
        raise HTTPException(404, "Not found")
    cid = l.course_id
    db.delete(l)
    db.commit()
    _sync_course(cid, db)
    return {"message": "Deleted"}


@router.post("/reorder")
def reorder(
    orders: list[dict],
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    for item in orders:
        l = db.query(Lesson).filter(Lesson.id == item["id"]).first()
        if l:
            l.sort_order = item["sort_order"]
    db.commit()
    return {"message": "Reordered"}


# ─────────────────────────────────────────────
# VIDEO PROGRESS
# ─────────────────────────────────────────────
@router.post("/{lesson_id}/video-progress")
def video_progress(
    lesson_id: int,
    req: VideoProgress,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    p = db.query(LessonProgress).filter(
        LessonProgress.user_id == user.id,
        LessonProgress.lesson_id == lesson_id
    ).first()
    if not p:
        p = LessonProgress(
            user_id=user.id,
            lesson_id=lesson_id,
            watch_seconds=req.watch_seconds
        )
        db.add(p)
    else:
        p.watch_seconds = max(p.watch_seconds, req.watch_seconds)
    db.commit()
    return {"watch_seconds": p.watch_seconds}


# ─────────────────────────────────────────────
# LESSON PROGRESS (completed status)
# ─────────────────────────────────────────────
@router.get("/{lesson_id}/progress")
def get_progress(
    lesson_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    p = db.query(LessonProgress).filter(
        LessonProgress.user_id == user.id,
        LessonProgress.lesson_id == lesson_id
    ).first()
    return {
        "lesson_id": lesson_id,
        "completed": p.completed if p else False,
        "watch_seconds": p.watch_seconds if p else 0
    }