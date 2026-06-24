"""
Game-like skill path with admin-managed subjects, topics, levels, and question sets.
"""
from datetime import datetime
import json
import math
import random
import re
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.ai_providers import call_ai
from core.database import get_db
from core.security import get_current_admin, get_current_user
from models.models import (
    PlacementAttempt,
    PlacementLevel,
    PlacementQuestion,
    PlacementSubject,
    PlacementTopic,
    User,
    UserPlacementProgress,
)

router = APIRouter()

PAID_PLANS = {"basic", "pro", "premium"}
SUPPORTED_TYPES = {"mcq", "fill_blank", "true_false", "error_correction", "sentence_reorder"}


class SubjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    sort_order: int = 0


class TopicCreate(BaseModel):
    subject_id: int
    name: str
    description: Optional[str] = None
    ai_prompt: Optional[str] = None
    sort_order: int = 0


class LevelCreate(BaseModel):
    topic_id: int
    title: str
    level_no: int = 1
    difficulty: str = "beginner"
    question_count: int = 5
    time_limit: int = 60
    hearts: int = 3
    pass_score: float = 60.0
    reward_xp: int = 20
    question_types: List[str] = Field(default_factory=lambda: ["mcq"])
    ai_prompt: Optional[str] = None
    is_boss: bool = False


class ManualQuestionCreate(BaseModel):
    level_id: int
    question_type: str = "mcq"
    prompt: str
    options: List[str]
    correct_index: int = 0
    explanation: Optional[str] = None


class AttemptSubmit(BaseModel):
    attempt_id: int
    answers: List[int]


def is_paid(user: User) -> bool:
    return user.role in ("admin", "superadmin") or (user.subscription_plan or "free") in PAID_PLANS


def serialize_subject(subject: PlacementSubject):
    return {
        "id": subject.id,
        "name": subject.name,
        "description": subject.description,
        "icon": subject.icon or "BOOK",
        "sort_order": subject.sort_order,
    }


def serialize_topic(topic: PlacementTopic):
    return {
        "id": topic.id,
        "subject_id": topic.subject_id,
        "name": topic.name,
        "description": topic.description,
        "ai_prompt": topic.ai_prompt,
        "sort_order": topic.sort_order,
    }


def serialize_level(level: PlacementLevel):
    return {
        "id": level.id,
        "topic_id": level.topic_id,
        "title": level.title,
        "level_no": level.level_no,
        "difficulty": level.difficulty,
        "question_count": level.question_count,
        "time_limit": level.time_limit,
        "hearts": level.hearts,
        "pass_score": level.pass_score,
        "reward_xp": level.reward_xp,
        "question_types": level.question_types or ["mcq"],
        "is_boss": level.is_boss,
        "ai_prompt": level.ai_prompt,
    }


def build_level_map(levels, progress_map, paid_user: bool):
    free_count = max(1, math.ceil(len(levels) * 0.3)) if levels else 0
    mapped = []
    previous_completed = True

    for index, level in enumerate(levels):
        progress = progress_map.get(level.id)
        free_level = index < free_count
        unlocked = previous_completed or index == 0
        requires_paid = (not free_level) and (not paid_user)
        mapped.append({
            **serialize_level(level),
            "is_free": free_level,
            "locked": not unlocked,
            "requires_paid": requires_paid,
            "playable": unlocked and not requires_paid,
            "completed": bool(progress.completed) if progress else False,
            "stars": progress.stars if progress else 0,
            "best_score": round(progress.best_score, 1) if progress else 0,
            "attempts_count": progress.attempts_count if progress else 0,
        })
        previous_completed = bool(progress.completed) if progress else False

    return mapped


def fallback_question(topic_name: str, level_title: str, question_type: str):
    base_topic = topic_name or "this skill"
    label = level_title or "Level"
    if question_type == "true_false":
        return {
            "type": "true_false",
            "question": f"{label}: {base_topic} improves through consistent practice.",
            "options": ["True", "False"],
            "correct_index": 0,
            "explanation": "Consistent practice is the best way to improve any language skill.",
        }
    if question_type == "fill_blank":
        return {
            "type": "fill_blank",
            "question": f"{label}: Choose the best word to complete the sentence about {base_topic}.",
            "options": ["correct", "wrong", "slowly", "never"],
            "correct_index": 0,
            "explanation": "The best answer is the one that keeps the sentence meaningful and accurate.",
        }
    if question_type == "sentence_reorder":
        return {
            "type": "sentence_reorder",
            "question": f"{label}: Which order makes the clearest sentence about {base_topic}?",
            "options": [
                f"I practice {base_topic} every day.",
                f"Practice I every day {base_topic}.",
                f"Every day I {base_topic} practice.",
                f"{base_topic} day every practice I.",
            ],
            "correct_index": 0,
            "explanation": "The correct answer follows natural English word order.",
        }
    if question_type == "error_correction":
        return {
            "type": "error_correction",
            "question": f"{label}: Which sentence is correct?",
            "options": [
                f"I am improving my {base_topic} skills.",
                f"I improving my {base_topic} skills.",
                f"I am improve my {base_topic} skills.",
                f"I improved my {base_topic} skills now.",
            ],
            "correct_index": 0,
            "explanation": "The correct answer uses natural verb form and sentence structure.",
        }
    return {
        "type": "mcq",
        "question": f"{label}: What is the best way to improve {base_topic}?",
        "options": [
            "Practice regularly and review mistakes.",
            "Skip feedback completely.",
            "Memorize random answers only.",
            "Avoid using the skill in context.",
        ],
        "correct_index": 0,
        "explanation": "Regular practice with feedback is the strongest improvement strategy.",
    }


async def generate_ai_questions(subject, topic, level, needed: int):
    types = [question_type for question_type in (level.question_types or ["mcq"]) if question_type in SUPPORTED_TYPES]
    system = (
        "You generate short game-like English learning questions. "
        f"Generate exactly {needed} questions as a JSON array with fields: "
        '"type", "question", "options", "correct_index", "explanation". '
        "Options must always be a JSON array. correct_index must point to one option."
    )
    prompt = (
        f"Subject: {subject.name}\n"
        f"Topic: {topic.name}\n"
        f"Level title: {level.title}\n"
        f"Difficulty: {level.difficulty}\n"
        f"Question types allowed: {json.dumps(types)}\n"
        f"Admin topic prompt: {topic.ai_prompt or ''}\n"
        f"Admin level prompt: {level.ai_prompt or ''}\n"
        "Return only valid JSON."
    )
    raw, _provider = await call_ai(system, [{"role": "user", "content": prompt}])
    raw = raw.strip()
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        raw = match.group()
    parsed = json.loads(raw)
    questions = []
    for item in parsed:
        options = item.get("options") or []
        correct_index = item.get("correct_index")
        if (
            isinstance(item.get("question"), str)
            and isinstance(options, list)
            and len(options) >= 2
            and isinstance(correct_index, int)
            and 0 <= correct_index < len(options)
        ):
            questions.append({
                "type": item.get("type") if item.get("type") in SUPPORTED_TYPES else "mcq",
                "question": item["question"],
                "options": options,
                "correct_index": correct_index,
                "explanation": item.get("explanation", ""),
            })
    return questions[:needed]


def get_nested_curriculum(db: Session):
    subjects = db.query(PlacementSubject).filter(PlacementSubject.is_active == True).order_by(
        PlacementSubject.sort_order.asc(), PlacementSubject.id.asc()
    ).all()
    topics = db.query(PlacementTopic).filter(PlacementTopic.is_active == True).order_by(
        PlacementTopic.sort_order.asc(), PlacementTopic.id.asc()
    ).all()
    levels = db.query(PlacementLevel).filter(PlacementLevel.is_active == True).order_by(
        PlacementLevel.topic_id.asc(), PlacementLevel.level_no.asc(), PlacementLevel.id.asc()
    ).all()
    question_counts = {
        level_id: count for level_id, count in db.query(
            PlacementQuestion.level_id, PlacementQuestion.id
        ).filter(PlacementQuestion.is_active == True).group_by(PlacementQuestion.level_id, PlacementQuestion.id).all()
    }

    topics_by_subject = {}
    for topic in topics:
        topics_by_subject.setdefault(topic.subject_id, []).append(topic)

    levels_by_topic = {}
    for level in levels:
        levels_by_topic.setdefault(level.topic_id, []).append(level)

    payload = []
    for subject in subjects:
        payload.append({
            **serialize_subject(subject),
            "topics": [
                {
                    **serialize_topic(topic),
                    "levels": [
                        {
                            **serialize_level(level),
                            "manual_question_count": question_counts.get(level.id, 0),
                        }
                        for level in levels_by_topic.get(topic.id, [])
                    ],
                }
                for topic in topics_by_subject.get(subject.id, [])
            ],
        })
    return payload


@router.get("/map")
def get_skill_map(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    subjects = db.query(PlacementSubject).filter(PlacementSubject.is_active == True).order_by(
        PlacementSubject.sort_order.asc(), PlacementSubject.id.asc()
    ).all()
    topics = db.query(PlacementTopic).filter(PlacementTopic.is_active == True).order_by(
        PlacementTopic.sort_order.asc(), PlacementTopic.id.asc()
    ).all()
    levels = db.query(PlacementLevel).filter(PlacementLevel.is_active == True).order_by(
        PlacementLevel.topic_id.asc(), PlacementLevel.level_no.asc(), PlacementLevel.id.asc()
    ).all()
    progress_rows = db.query(UserPlacementProgress).filter(UserPlacementProgress.user_id == user.id).all()
    progress_map = {row.level_id: row for row in progress_rows}
    paid_user = is_paid(user)

    topics_by_subject = {}
    for topic in topics:
        topics_by_subject.setdefault(topic.subject_id, []).append(topic)

    levels_by_topic = {}
    for level in levels:
        levels_by_topic.setdefault(level.topic_id, []).append(level)

    structured = []
    total_levels = 0
    completed_levels = 0
    for subject in subjects:
        topic_payload = []
        for topic in topics_by_subject.get(subject.id, []):
            mapped_levels = build_level_map(levels_by_topic.get(topic.id, []), progress_map, paid_user)
            total_levels += len(mapped_levels)
            completed_levels += sum(1 for item in mapped_levels if item["completed"])
            topic_payload.append({
                **serialize_topic(topic),
                "levels": mapped_levels,
            })
        structured.append({
            **serialize_subject(subject),
            "topics": topic_payload,
        })

    next_free = None
    for subject in structured:
        for topic in subject["topics"]:
            for level in topic["levels"]:
                if level["playable"] and not level["completed"]:
                    next_free = {
                        "subject_name": subject["name"],
                        "topic_name": topic["name"],
                        "level_id": level["id"],
                        "level_title": level["title"],
                        "is_boss": level["is_boss"],
                    }
                    break
            if next_free:
                break
        if next_free:
            break

    missions = {
        "daily": [
            "Complete 2 path levels",
            "Beat 1 boss level",
            "Keep at least 1 heart left in a run",
        ],
        "completed_levels": completed_levels,
        "total_levels": total_levels,
    }

    return {
        "subjects": structured,
        "next_level": next_free,
        "plan": user.subscription_plan or "free",
        "is_paid": paid_user,
        "free_access_pct": 30,
        "missions": missions,
    }


@router.get("/questions")
def get_placement_questions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get quick placement test questions without creating an attempt"""
    placement_questions = [
        {
            "id": 1,
            "level": "A1",
            "question": "What is your name?",
            "options": ["My name is John", "I am student", "Yes, I'm here", "That's correct"],
            "correct_answer": "My name is John"
        },
        {
            "id": 2,
            "level": "A1",
            "question": "How are you?",
            "options": ["I'm fine, thank you", "Yes, I am", "The weather is good", "No, I'm here"],
            "correct_answer": "I'm fine, thank you"
        },
        {
            "id": 3,
            "level": "A2",
            "question": "Where do you work?",
            "options": ["I work in an office", "I like working", "Working is important", "Yes, I do"],
            "correct_answer": "I work in an office"
        },
        {
            "id": 4,
            "level": "A2",
            "question": "Have you visited Paris?",
            "options": ["Yes, I have been there", "Yes, I go there", "I visit Paris", "I'm visiting Paris"],
            "correct_answer": "Yes, I have been there"
        },
        {
            "id": 5,
            "level": "B1",
            "question": "If I had more time, I would _____ a novel.",
            "options": ["write", "to write", "be writing", "written"],
            "correct_answer": "write"
        },
        {
            "id": 6,
            "level": "B1",
            "question": "She suggested that I _____ more exercise.",
            "options": ["take", "took", "should take", "taking"],
            "correct_answer": "take"
        },
        {
            "id": 7,
            "level": "B2",
            "question": "Despite _____ warning, he continued with his plan.",
            "options": ["their", "them", "they", "themselves"],
            "correct_answer": "their"
        },
        {
            "id": 8,
            "level": "B2",
            "question": "The project was so ambitious that it _____ months of planning.",
            "options": ["necessitated", "needed", "required", "demanded"],
            "correct_answer": "necessitated"
        },
        {
            "id": 9,
            "level": "C1",
            "question": "His _____ behavior at the meeting was deemed unprofessional by his colleagues.",
            "options": ["obtuse", "obtuse", "obsequious", "obfuscated"],
            "correct_answer": "obtuse"
        },
        {
            "id": 10,
            "level": "C1",
            "question": "The author's arguments, while _____, were ultimately unconvincing.",
            "options": ["cogent", "pellucid", "sagacious", "perspicacious"],
            "correct_answer": "cogent"
        }
    ]
    
    return {"questions": placement_questions}


@router.get("/questions-public")
def get_placement_questions_public():
    """PUBLIC endpoint - Get quick placement test questions without authentication"""
    placement_questions = [
        {
            "id": 1,
            "level": "A1",
            "question": "What is your name?",
            "options": ["My name is John", "I am student", "Yes, I'm here", "That's correct"],
            "correct_answer": "My name is John"
        },
        {
            "id": 2,
            "level": "A1",
            "question": "How are you?",
            "options": ["I'm fine, thank you", "Yes, I am", "The weather is good", "No, I'm here"],
            "correct_answer": "I'm fine, thank you"
        },
        {
            "id": 3,
            "level": "A2",
            "question": "Where do you work?",
            "options": ["I work in an office", "I like working", "Working is important", "Yes, I do"],
            "correct_answer": "I work in an office"
        },
        {
            "id": 4,
            "level": "A2",
            "question": "Have you visited Paris?",
            "options": ["Yes, I have been there", "Yes, I go there", "I visit Paris", "I'm visiting Paris"],
            "correct_answer": "Yes, I have been there"
        },
        {
            "id": 5,
            "level": "B1",
            "question": "If I had more time, I would _____ a novel.",
            "options": ["write", "to write", "be writing", "written"],
            "correct_answer": "write"
        },
        {
            "id": 6,
            "level": "B1",
            "question": "She suggested that I _____ more exercise.",
            "options": ["take", "took", "should take", "taking"],
            "correct_answer": "take"
        },
        {
            "id": 7,
            "level": "B2",
            "question": "Despite _____ warning, he continued with his plan.",
            "options": ["their", "them", "they", "themselves"],
            "correct_answer": "their"
        },
        {
            "id": 8,
            "level": "B2",
            "question": "The project was so ambitious that it _____ months of planning.",
            "options": ["necessitated", "needed", "required", "demanded"],
            "correct_answer": "necessitated"
        },
        {
            "id": 9,
            "level": "C1",
            "question": "His _____ behavior at the meeting was deemed unprofessional by his colleagues.",
            "options": ["obtuse", "obtuse", "obsequious", "obfuscated"],
            "correct_answer": "obtuse"
        },
        {
            "id": 10,
            "level": "C1",
            "question": "The author's arguments, while _____, were ultimately unconvincing.",
            "options": ["cogent", "pellucid", "sagacious", "perspicacious"],
            "correct_answer": "cogent"
        }
    ]
    
    return {"questions": placement_questions}


@router.get("/pub/test")
def pub_test():
    questions = [
        {"id": 1, "level": "A1", "question": "What is your name?", "options": ["My name is John", "I am student", "Yes, I'm here", "That's correct"]},
        {"id": 2, "level": "A1", "question": "How are you?", "options": ["I'm fine, thank you", "Yes, I am", "The weather is good", "No, I'm here"]},
        {"id": 3, "level": "A2", "question": "Where do you work?", "options": ["I work in an office", "I like working", "Working is important", "Yes, I do"]},
        {"id": 4, "level": "A2", "question": "Have you visited Paris?", "options": ["Yes, I have been there", "Yes, I go there", "I visit Paris", "I'm visiting Paris"]},
        {"id": 5, "level": "B1", "question": "If I had more time, I would _____ a novel.", "options": ["write", "to write", "be writing", "written"]},
        {"id": 6, "level": "B1", "question": "She suggested that I _____ more exercise.", "options": ["take", "took", "should take", "taking"]},
        {"id": 7, "level": "B2", "question": "Despite _____ warning, he continued with his plan.", "options": ["their", "them", "they", "themselves"]},
        {"id": 8, "level": "B2", "question": "The project was so ambitious that it _____ months of planning.", "options": ["necessitated", "needed", "required", "demanded"]},
        {"id": 9, "level": "C1", "question": "His _____ behavior was deemed unprofessional.", "options": ["obtuse", "obvious", "obsequious", "obfuscated"]},
        {"id": 10, "level": "C1", "question": "The author's arguments were ultimately unconvincing.", "options": ["cogent", "pellucid", "sagacious", "perspicacious"]},
    ]
    return {"working": True, "questions": questions}


@router.post("/start/{level_id}")
async def start_level(level_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    level = db.query(PlacementLevel).filter(PlacementLevel.id == level_id, PlacementLevel.is_active == True).first()
    if not level:
        raise HTTPException(404, "Level not found")
    topic = db.query(PlacementTopic).filter(PlacementTopic.id == level.topic_id, PlacementTopic.is_active == True).first()
    subject = db.query(PlacementSubject).filter(
        PlacementSubject.id == topic.subject_id, PlacementSubject.is_active == True
    ).first() if topic else None
    if not topic or not subject:
        raise HTTPException(404, "Level path not found")

    topic_levels = db.query(PlacementLevel).filter(
        PlacementLevel.topic_id == topic.id,
        PlacementLevel.is_active == True
    ).order_by(PlacementLevel.level_no.asc(), PlacementLevel.id.asc()).all()
    progress_map = {
        row.level_id: row for row in db.query(UserPlacementProgress).filter(UserPlacementProgress.user_id == user.id).all()
    }
    mapped_levels = build_level_map(topic_levels, progress_map, is_paid(user))
    level_state = next((item for item in mapped_levels if item["id"] == level_id), None)
    if not level_state or level_state["locked"]:
        raise HTTPException(403, "Complete previous level first")
    if level_state["requires_paid"]:
        raise HTTPException(402, "This premium path unlocks after the free 30% preview")

    manual_questions = db.query(PlacementQuestion).filter(
        PlacementQuestion.level_id == level.id,
        PlacementQuestion.is_active == True
    ).all()
    manual_payload = [{
        "type": item.question_type if item.question_type in SUPPORTED_TYPES else "mcq",
        "question": item.prompt,
        "options": item.options or [],
        "correct_index": item.correct_index,
        "explanation": item.explanation or "",
    } for item in manual_questions]
    random.shuffle(manual_payload)

    needed = max(3, level.question_count)
    questions = manual_payload[:needed]
    if len(questions) < needed:
        try:
            ai_questions = await generate_ai_questions(subject, topic, level, needed - len(questions))
            questions.extend(ai_questions)
        except Exception:
            pass

    while len(questions) < needed:
        questions.append(fallback_question(topic.name, level.title, random.choice(level.question_types or ["mcq"])))

    attempt = PlacementAttempt(
        user_id=user.id,
        level_id=level.id,
        questions=questions[:needed],
        hearts_left=level.hearts,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    public_questions = [{
        "question": item["question"],
        "type": item.get("type", "mcq"),
        "options": item.get("options") or [],
    } for item in questions[:needed]]
    return {
        "attempt_id": attempt.id,
        "level": serialize_level(level),
        "topic": serialize_topic(topic),
        "subject": serialize_subject(subject),
        "questions": public_questions,
    }


@router.post("/submit")
def submit_attempt(req: AttemptSubmit, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    attempt = db.query(PlacementAttempt).filter(
        PlacementAttempt.id == req.attempt_id,
        PlacementAttempt.user_id == user.id,
    ).first()
    if not attempt:
        raise HTTPException(404, "Attempt not found")
    if attempt.completed_at:
        raise HTTPException(400, "Attempt already submitted")

    level = db.query(PlacementLevel).filter(PlacementLevel.id == attempt.level_id).first()
    if not level:
        raise HTTPException(404, "Level not found")

    questions = attempt.questions or []
    if len(req.answers) != len(questions):
        raise HTTPException(400, f"Expected {len(questions)} answers")

    correct = 0
    feedback = []
    for question, answer in zip(questions, req.answers):
        options = question.get("options") or []
        correct_index = question.get("correct_index", 0)
        is_correct = answer == correct_index
        if is_correct:
            correct += 1
        feedback.append({
            "question": question.get("question", ""),
            "your_answer": options[answer] if 0 <= answer < len(options) else "Invalid",
            "correct_answer": options[correct_index] if 0 <= correct_index < len(options) else "",
            "is_correct": is_correct,
            "explanation": question.get("explanation", ""),
        })

    score = round((correct / max(1, len(questions))) * 100, 1)
    wrong_count = max(0, len(questions) - correct)
    hearts_left = max(0, level.hearts - wrong_count)
    passed = score >= level.pass_score and hearts_left > 0
    if not passed:
        stars = 0
    elif score >= 95 and hearts_left == level.hearts:
        stars = 3
    elif score >= max(level.pass_score + 15, 75):
        stars = 2
    else:
        stars = 1

    xp_earned = 5
    if passed:
        xp_earned = level.reward_xp + (10 if stars == 3 else 5 if stars == 2 else 0)

    attempt.answers = req.answers
    attempt.score = score
    attempt.stars = stars
    attempt.hearts_left = hearts_left
    attempt.xp_earned = xp_earned
    attempt.passed = passed
    attempt.completed_at = datetime.utcnow()

    progress = db.query(UserPlacementProgress).filter(
        UserPlacementProgress.user_id == user.id,
        UserPlacementProgress.level_id == level.id,
    ).first()
    if not progress:
        progress = UserPlacementProgress(user_id=user.id, level_id=level.id)
        db.add(progress)

    progress.attempts_count += 1
    progress.best_score = max(progress.best_score or 0, score)
    progress.stars = max(progress.stars or 0, stars)
    progress.completed = progress.completed or passed
    progress.last_played_at = datetime.utcnow()

    user.xp_points += xp_earned
    db.commit()

    next_level = db.query(PlacementLevel).filter(
        PlacementLevel.topic_id == level.topic_id,
        PlacementLevel.level_no > level.level_no,
        PlacementLevel.is_active == True,
    ).order_by(PlacementLevel.level_no.asc(), PlacementLevel.id.asc()).first()

    return {
        "score": score,
        "correct": correct,
        "total": len(questions),
        "passed": passed,
        "stars": stars,
        "hearts_left": hearts_left,
        "xp_earned": xp_earned,
        "feedback": feedback,
        "next_level_id": next_level.id if next_level and passed else None,
    }


class PlacementSubmitSimple(BaseModel):
    answers: List[int]


@router.post("/submit-simple")
def submit_placement_test(req: PlacementSubmitSimple, user: User = Depends(get_current_user)):
    """Simple placement test submission without attempt tracking"""
    # Correct answers for each question
    correct_answers = [
        0,  # Q1: My name is John
        0,  # Q2: I'm fine, thank you
        0,  # Q3: I work in an office
        0,  # Q4: Yes, I have been there
        0,  # Q5: write
        0,  # Q6: take
        0,  # Q7: their
        0,  # Q8: necessitated
        0,  # Q9: obtuse
        0,  # Q10: cogent
    ]
    
    # Map levels to assigned level based on score
    level_map = {
        0: "A1",
        1: "A1",
        2: "A1",
        3: "A2",
        4: "A2",
        5: "B1",
        6: "B1",
        7: "B2",
        8: "B2",
        9: "C1",
    }
    
    # Q to level map for results
    q_to_level = [
        "A1", "A1", "A2", "A2", "B1", "B1", "B2", "B2", "C1", "C1"
    ]
    
    # Calculate score
    correct = sum(1 for i, ans in enumerate(req.answers) if i < len(correct_answers) and ans == correct_answers[i])
    total = len(correct_answers)
    score = round((correct / total) * 100, 1)
    
    # Determine assigned level based on highest correct level
    assigned_level = "A1"
    for i, ans in enumerate(req.answers):
        if i < len(correct_answers) and ans == correct_answers[i]:
            assigned_level = q_to_level[i]
    
    # Create detailed results
    results = []
    for i, ans in enumerate(req.answers):
        if i < len(correct_answers):
            question_options = [
                ["My name is John", "I am student", "Yes, I'm here", "That's correct"],
                ["I'm fine, thank you", "Yes, I am", "The weather is good", "No, I'm here"],
                ["I work in an office", "I like working", "Working is important", "Yes, I do"],
                ["Yes, I have been there", "Yes, I go there", "I visit Paris", "I'm visiting Paris"],
                ["write", "to write", "be writing", "written"],
                ["take", "took", "should take", "taking"],
                ["their", "them", "they", "themselves"],
                ["necessitated", "needed", "required", "demanded"],
                ["obtuse", "obtuse", "obsequious", "obfuscated"],
                ["cogent", "pellucid", "sagacious", "perspicacious"],
            ]
            questions = [
                "What is your name?",
                "How are you?",
                "Where do you work?",
                "Have you visited Paris?",
                "If I had more time, I would _____ a novel.",
                "She suggested that I _____ more exercise.",
                "Despite _____ warning, he continued with his plan.",
                "The project was so ambitious that it _____ months of planning.",
                "His _____ behavior at the meeting was deemed unprofessional.",
                "The author's arguments, while _____, were ultimately unconvincing.",
            ]
            explanations = [
                "Simple greeting - correct form to introduce yourself.",
                "Standard response to 'How are you?' in English.",
                "Correct preposition and verb form for job location.",
                "Perfect tense is used for experiences in the past.",
                "Conditional requires base verb form after 'would'.",
                "Subjunctive mood requires base verb form.",
                "Possessive adjective needed before a noun.",
                "Formal vocabulary choice that fits the context.",
                "Word meaning unclear or confused in judgment.",
                "Means clear or well-organized; appropriate here.",
            ]
            
            is_correct = ans == correct_answers[i]
            results.append({
                "question_id": i + 1,
                "question_text": questions[i],
                "level": q_to_level[i],
                "is_correct": is_correct,
                "your_answer": question_options[i][ans] if ans < len(question_options[i]) else "Invalid",
                "correct_answer": question_options[i][correct_answers[i]],
                "explanation": explanations[i],
            })
    
    xp_earned = int(score * 1.5)  # Score-based XP
    
    return {
        "score": score,
        "correct": correct,
        "total": total,
        "level_assigned": assigned_level,
        "xp_earned": xp_earned,
        "message": f"You reached {assigned_level} level!",
        "recommended_course_level": assigned_level,
        "results": results,
    }


@router.get("/admin/curriculum")
def admin_curriculum(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return {"subjects": get_nested_curriculum(db)}


@router.post("/admin/subjects")
def create_subject(req: SubjectCreate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    subject = PlacementSubject(
        name=req.name.strip(),
        description=req.description,
        icon=req.icon,
        sort_order=req.sort_order,
    )
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return serialize_subject(subject)


@router.post("/admin/topics")
def create_topic(req: TopicCreate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    subject = db.query(PlacementSubject).filter(PlacementSubject.id == req.subject_id).first()
    if not subject:
        raise HTTPException(404, "Subject not found")
    topic = PlacementTopic(
        subject_id=req.subject_id,
        name=req.name.strip(),
        description=req.description,
        ai_prompt=req.ai_prompt,
        sort_order=req.sort_order,
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return serialize_topic(topic)


@router.post("/admin/levels")
def create_level(req: LevelCreate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    topic = db.query(PlacementTopic).filter(PlacementTopic.id == req.topic_id).first()
    if not topic:
        raise HTTPException(404, "Topic not found")
    clean_types = [item for item in req.question_types if item in SUPPORTED_TYPES] or ["mcq"]
    level = PlacementLevel(
        topic_id=req.topic_id,
        title=req.title.strip(),
        level_no=req.level_no,
        difficulty=req.difficulty,
        question_count=max(3, req.question_count),
        time_limit=max(20, req.time_limit),
        hearts=max(1, req.hearts),
        pass_score=max(10, min(req.pass_score, 100)),
        reward_xp=max(5, req.reward_xp),
        question_types=clean_types,
        ai_prompt=req.ai_prompt,
        is_boss=req.is_boss,
    )
    db.add(level)
    db.commit()
    db.refresh(level)
    return serialize_level(level)


@router.post("/admin/questions")
def create_manual_question(req: ManualQuestionCreate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    level = db.query(PlacementLevel).filter(PlacementLevel.id == req.level_id).first()
    if not level:
        raise HTTPException(404, "Level not found")
    if req.question_type not in SUPPORTED_TYPES:
        raise HTTPException(400, "Unsupported question type")
    if len(req.options) < 2:
        raise HTTPException(400, "At least 2 options required")
    if req.correct_index < 0 or req.correct_index >= len(req.options):
        raise HTTPException(400, "correct_index out of range")

    question = PlacementQuestion(
        level_id=req.level_id,
        question_type=req.question_type,
        prompt=req.prompt.strip(),
        options=req.options,
        correct_index=req.correct_index,
        explanation=req.explanation,
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return {
        "id": question.id,
        "level_id": question.level_id,
        "question_type": question.question_type,
        "prompt": question.prompt,
    }
