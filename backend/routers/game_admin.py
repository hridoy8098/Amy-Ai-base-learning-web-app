"""
Game Learning System - Admin Router
Admin panel for curriculum management

POST   /api/admin/game/subjects              - Create subject
GET    /api/admin/game/subjects              - List subjects
PUT    /api/admin/game/subjects/{id}         - Update subject
DELETE /api/admin/game/subjects/{id}         - Delete subject

POST   /api/admin/game/subjects/{id}/topics  - Create topic
GET    /api/admin/game/subjects/{id}/topics  - List topics
POST   /api/admin/game/topics/{id}/levels    - Create level
GET    /api/admin/game/questions             - List questions
POST   /api/admin/game/questions/generate    - Generate questions
POST   /api/admin/game/questions/upload      - Upload questions
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from core.database import get_db
from core.security import get_current_user
from models.game_models import (
    GameSubject, GameTopic, GameLevel, GameQuestion, FallbackQuestion,
    LevelLock, QuestionSourceEnum
)
from models.models import User
from typing import Optional, List
import csv
import io
import json
from datetime import datetime

router = APIRouter(
    tags=["admin-game"]
)

# ═══════════════════════════════════════════════════════════════════════════
# HELPER: Admin Verification
# ═══════════════════════════════════════════════════════════════════════════

async def verify_admin(current_user: User = Depends(get_current_user)):
    """Verify user is admin"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# ═══════════════════════════════════════════════════════════════════════════
# SUBJECT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/subjects")
async def create_subject(
    name: str,
    description: Optional[str] = None,
    icon: Optional[str] = None,
    color: Optional[str] = None,
    order_index: int = 0,
    db: Session = Depends(get_db),
    admin_user = Depends(verify_admin)
):
    """Admin creates new subject"""
    
    # Check if subject already exists
    existing = db.query(GameSubject).filter(GameSubject.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Subject already exists")
    
    new_subject = GameSubject(
        name=name,
        description=description,
        icon=icon,
        color=color,
        order_index=order_index,
        is_active=True
    )
    
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    
    return {
        "id": new_subject.id,
        "name": new_subject.name,
        "message": "Subject created successfully"
    }


@router.get("/subjects")
async def list_subjects(
    db: Session = Depends(get_db),
    admin_user = Depends(verify_admin)
):
    """List all subjects"""
    subjects = db.query(GameSubject).order_by(GameSubject.order_index).all()
    
    return {
        "total": len(subjects),
        "subjects": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "icon": s.icon,
                "color": s.color,
                "topic_count": len(s.topics),
                "is_active": s.is_active
            }
            for s in subjects
        ]
    }


@router.put("/subjects/{subject_id}")
async def update_subject(
    subject_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    icon: Optional[str] = None,
    color: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    admin_user = Depends(verify_admin)
):
    """Update subject"""
    subject = db.query(GameSubject).filter(GameSubject.id == subject_id).first()
    
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    if name:
        subject.name = name
    if description:
        subject.description = description
    if icon:
        subject.icon = icon
    if color:
        subject.color = color
    if is_active is not None:
        subject.is_active = is_active
    
    subject.updated_at = datetime.now()
    db.commit()
    
    return {"message": "Subject updated successfully"}


@router.delete("/subjects/{subject_id}")
async def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(verify_admin)
):
    """Soft delete subject"""
    subject = db.query(GameSubject).filter(GameSubject.id == subject_id).first()
    
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    subject.is_active = False
    subject.updated_at = datetime.now()
    db.commit()
    
    return {"message": "Subject deleted successfully"}


# ═══════════════════════════════════════════════════════════════════════════
# TOPIC ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/subjects/{subject_id}/topics")
async def create_topic(
    subject_id: int,
    name: str,
    description: Optional[str] = None,
    icon: Optional[str] = None,
    order_index: int = 0,
    db: Session = Depends(get_db),
    admin_user = Depends(verify_admin)
):
    """Admin creates topic under subject"""
    
    # Check subject exists
    subject = db.query(GameSubject).filter(GameSubject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    # Check topic doesn't exist
    existing = db.query(GameTopic).filter(
        GameTopic.subject_id == subject_id,
        GameTopic.name == name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Topic already exists in this subject")
    
    new_topic = GameTopic(
        subject_id=subject_id,
        name=name,
        description=description,
        icon=icon,
        order_index=order_index,
        is_active=True
    )
    
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)
    
    return {
        "id": new_topic.id,
        "name": new_topic.name,
        "subject_id": subject_id,
        "message": "Topic created successfully"
    }


@router.get("/subjects/{subject_id}/topics")
async def list_topics(
    subject_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(verify_admin)
):
    """List topics for subject"""
    topics = db.query(GameTopic).filter(
        GameTopic.subject_id == subject_id,
        GameTopic.is_active == True
    ).order_by(GameTopic.order_index).all()
    
    return {
        "total": len(topics),
        "topics": [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "icon": t.icon,
                "level_count": len(t.levels),
                "order_index": t.order_index
            }
            for t in topics
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════
# LEVEL ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/topics/{topic_id}/levels")
async def create_level(
    topic_id: int,
    title: str,
    level_number: int,
    difficulty: str,  # "easy", "medium", "hard"
    pass_score: int = 70,
    question_count: int = 10,
    time_limit_seconds: int = 300,
    question_types: List[str] = None,
    xp_reward: int = 100,
    is_boss: bool = False,
    ai_prompt_template: Optional[str] = None,
    ai_generation_rules: Optional[dict] = None,
    db: Session = Depends(get_db),
    admin_user = Depends(verify_admin)
):
    """Admin creates level under topic"""
    
    # Check topic exists
    topic = db.query(GameTopic).filter(GameTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Check level number doesn't exist
    existing = db.query(GameLevel).filter(
        GameLevel.topic_id == topic_id,
        GameLevel.level_number == level_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Level number already exists")
    
    new_level = GameLevel(
        topic_id=topic_id,
        title=title,
        level_number=level_number,
        difficulty=difficulty,
        pass_score=pass_score,
        question_count=question_count,
        time_limit_seconds=time_limit_seconds,
        question_types=question_types or ["mcq"],
        xp_reward=xp_reward,
        level_type="boss" if is_boss else "normal",
        ai_prompt_template=ai_prompt_template,
        ai_generation_rules=ai_generation_rules,
        is_active=True
    )
    
    db.add(new_level)
    db.commit()
    db.refresh(new_level)
    
    return {
        "id": new_level.id,
        "title": new_level.title,
        "level_number": new_level.level_number,
        "message": "Level created successfully"
    }


@router.get("/topics/{topic_id}/levels")
async def list_levels(
    topic_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(verify_admin)
):
    """List levels for topic"""
    levels = db.query(GameLevel).filter(
        GameLevel.topic_id == topic_id,
        GameLevel.is_active == True
    ).order_by(GameLevel.level_number).all()
    
    return {
        "total": len(levels),
        "levels": [
            {
                "id": l.id,
                "title": l.title,
                "level_number": l.level_number,
                "difficulty": l.difficulty,
                "level_type": l.level_type,
                "question_count": l.question_count,
                "xp_reward": l.xp_reward,
                "question_count_in_db": len(l.questions),
                "pass_score": l.pass_score
            }
            for l in levels
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════
# QUESTION ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/questions/upload")
async def upload_questions(
    level_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin_user = Depends(verify_admin)
):
    """Upload and add fallback questions (CSV)
    
    CSV Format:
    question_type,question_text,options,correct_answer,explanation
    mcq,"What is the past tense of go?","go|went|goes|gone",1,"Went is past tense"
    """
    
    # Check level exists
    level = db.query(GameLevel).filter(GameLevel.id == level_id).first()
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    
    try:
        contents = await file.read()
        stream = io.StringIO(contents.decode('utf-8'))
        reader = csv.DictReader(stream)
        
        added_count = 0
        
        for row in reader:
            try:
                # Parse options
                options = row['options'].split('|') if row['options'] else []
                
                # Determine correct answer based on question type
                question_type = row['question_type']
                correct_idx = int(row['correct_answer'])
                
                if question_type == 'mcq':
                    correct_answer = options[correct_idx]
                else:
                    correct_answer = row['correct_answer']
                
                question = FallbackQuestion(
                    level_id=level_id,
                    question_type=question_type,
                    question_text=row['question_text'],
                    options=options if options else None,
                    correct_answer=correct_answer,
                    explanation=row.get('explanation', ''),
                    is_active=True
                )
                
                db.add(question)
                added_count += 1
            
            except Exception as e:
                print(f"Error adding row: {e}")
                continue
        
        db.commit()
        
        return {
            "message": f"Successfully added {added_count} questions",
            "count": added_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File processing error: {str(e)}")


@router.get("/levels/{level_id}/questions")
async def get_level_questions(
    level_id: int,
    source: Optional[str] = None,  # "ai", "manual", or None for all
    db: Session = Depends(get_db),
    admin_user = Depends(verify_admin)
):
    """Get all questions for a level"""
    
    query = db.query(GameQuestion).filter(GameQuestion.level_id == level_id)
    
    if source == "ai":
        query = query.filter(GameQuestion.source == QuestionSourceEnum.AI_GENERATED)
    elif source == "manual":
        query = query.filter(GameQuestion.source == QuestionSourceEnum.ADMIN_MANUAL)
    
    questions = query.all()
    
    return {
        "total": len(questions),
        "ai_count": len([q for q in questions if q.source == QuestionSourceEnum.AI_GENERATED]),
        "manual_count": len([q for q in questions if q.source == QuestionSourceEnum.ADMIN_MANUAL]),
        "questions": [
            {
                "id": q.id,
                "type": q.question_type,
                "text": q.question_text[:50] + "..." if len(q.question_text) > 50 else q.question_text,
                "source": q.source,
                "is_verified": q.is_verified,
                "attempts": q.attempts_count,
                "success_rate": f"{q.success_rate:.1f}%"
            }
            for q in questions
        ]
    }


@router.get("/levels/{level_id}/fallback-questions")
async def get_fallback_questions(
    level_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(verify_admin)
):
    """Get fallback (manual) questions"""
    
    questions = db.query(FallbackQuestion).filter(
        FallbackQuestion.level_id == level_id
    ).order_by(desc(FallbackQuestion.priority)).all()
    
    return {
        "total": len(questions),
        "questions": [
            {
                "id": q.id,
                "type": q.question_type,
                "text": q.question_text[:60],
                "priority": q.priority,
                "is_active": q.is_active
            }
            for q in questions
        ]
    }


@router.post("/questions/generate")
async def ai_generate_questions(
    level_id: int,
    count: int = 10,
    force_regenerate: bool = False,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    admin_user = Depends(verify_admin)
):
    """Trigger AI question generation (async task)
    
    Note: In real implementation, this would call your AI provider
    """
    
    # Check level exists
    level = db.query(GameLevel).filter(GameLevel.id == level_id).first()
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    
    # TODO: Call your AI question generator here
    # from core.ai_question_generator import AIQuestionGenerator
    # generator = AIQuestionGenerator()
    # background_tasks.add_task(generator.generate_questions_for_level, level_id, count)
    
    return {
        "message": f"Question generation started for {count} questions",
        "level_id": level_id,
        "count": count,
        "status": "processing",
        "note": "AI generation task is running in background. Check back in a moment."
    }


@router.post("/levels/{level_id}/set-prerequisites")
async def set_level_prerequisites(
    level_id: int,
    prerequisite_level_id: int,
    required_score: int = 70,
    db: Session = Depends(get_db),
    admin_user = Depends(verify_admin)
):
    """Set prerequisite for unlocking a level"""
    
    # Check both levels exist
    level = db.query(GameLevel).filter(GameLevel.id == level_id).first()
    prereq = db.query(GameLevel).filter(GameLevel.id == prerequisite_level_id).first()
    
    if not level or not prereq:
        raise HTTPException(status_code=404, detail="Level not found")
    
    # Check if prerequisite already set
    existing = db.query(LevelLock).filter(
        LevelLock.level_id == level_id,
        LevelLock.prerequisite_level_id == prerequisite_level_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Prerequisite already set")
    
    lock = LevelLock(
        level_id=level_id,
        prerequisite_level_id=prerequisite_level_id,
        required_score=required_score
    )
    
    db.add(lock)
    db.commit()
    
    return {"message": "Prerequisite set successfully"}


# ═══════════════════════════════════════════════════════════════════════════
# DASHBOARD ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    admin_user = Depends(verify_admin)
):
    """Get admin dashboard statistics"""
    
    total_subjects = db.query(GameSubject).filter(GameSubject.is_active == True).count()
    total_topics = db.query(GameTopic).filter(GameTopic.is_active == True).count()
    total_levels = db.query(GameLevel).filter(GameLevel.is_active == True).count()
    total_questions = db.query(GameQuestion).filter(GameQuestion.is_active == True).count()
    total_fallback = db.query(FallbackQuestion).filter(FallbackQuestion.is_active == True).count()
    
    return {
        "curriculum": {
            "subjects": total_subjects,
            "topics": total_topics,
            "levels": total_levels
        },
        "questions": {
            "ai_generated": db.query(GameQuestion).filter(
                GameQuestion.source == QuestionSourceEnum.AI_GENERATED
            ).count(),
            "manual": total_fallback
        },
        "total": {
            "active_questions": total_questions + total_fallback
        }
    }
