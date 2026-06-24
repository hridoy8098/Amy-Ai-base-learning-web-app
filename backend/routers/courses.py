from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from core.database import get_db
from core.security import get_current_user, get_current_admin, get_optional_user
from models.models import Course, Lesson, Enrollment, LessonProgress, CourseReview, User
from datetime import datetime
import re

router = APIRouter()

def slugify(text):
    text=text.lower().strip()
    text=re.sub(r'[^\w\s-]','',text)
    text=re.sub(r'[\s_-]+','-',text)
    return text

class CourseCreate(BaseModel):
    title: str; description: Optional[str]=None; short_desc: Optional[str]=None
    thumbnail: Optional[str]=None; level: str="beginner"; language: str="en"
    is_free: bool=False; price: float=0.0; discount_price: Optional[float]=None
    category_id: Optional[int]=None; status: str="draft"
    what_you_learn: Optional[List[str]]=None
    requirements: Optional[List[str]]=None
    tags: Optional[List[str]]=None

class CourseUpdate(BaseModel):
    title: Optional[str]=None; description: Optional[str]=None
    short_desc: Optional[str]=None; thumbnail: Optional[str]=None
    level: Optional[str]=None; language: Optional[str]=None
    is_free: Optional[bool]=None; price: Optional[float]=None
    discount_price: Optional[float]=None; category_id: Optional[int]=None
    status: Optional[str]=None; what_you_learn: Optional[List[str]]=None
    requirements: Optional[List[str]]=None; tags: Optional[List[str]]=None

class ReviewCreate(BaseModel):
    rating: int; comment: Optional[str]=None

def _course(c, user=None, db=None):
    enrolled=False; progress=0.0
    if user and db:
        enr=db.query(Enrollment).filter(Enrollment.user_id==user.id,Enrollment.course_id==c.id).first()
        if enr: enrolled=True; progress=enr.progress
    return {
        "id":c.id,"title":c.title,"slug":c.slug,"description":c.description,
        "short_desc":c.short_desc,"thumbnail":c.thumbnail,"level":c.level,
        "language":c.language,"status":c.status,"is_free":c.is_free,
        "price":c.price,"discount_price":c.discount_price,
        "total_lessons":c.total_lessons,"total_duration":c.total_duration,
        "enrolled_count":c.enrolled_count,"rating_avg":c.rating_avg,
        "rating_count":c.rating_count,"what_you_learn":c.what_you_learn,
        "requirements":c.requirements,"tags":c.tags,
        "category_id":c.category_id,
        "category_name":c.category.name if c.category else None,
        "instructor_id":c.instructor_id,
        "instructor_name":c.instructor.name if c.instructor else None,
        "enrolled":enrolled,"progress":progress,
        "created_at":c.created_at.isoformat() if c.created_at else None,
    }

def _update_level(u):
    for i,t in enumerate([0,100,300,600,1000,1500,2200,3000,4000,5500,7500]):
        if u.xp_points>=t: u.level=i+1

@router.get("")
def list_courses(
    category_id: Optional[int]=None, level: Optional[str]=None,
    is_free: Optional[bool]=None, search: Optional[str]=None,
    page: int=Query(1,ge=1), limit: int=Query(12,ge=1,le=50),
    db=Depends(get_db), user=Depends(get_optional_user),
):
    q=db.query(Course).filter(Course.status=="published")
    if category_id: q=q.filter(Course.category_id==category_id)
    if level:       q=q.filter(Course.level==level)
    if is_free is not None: q=q.filter(Course.is_free==is_free)
    if search:      q=q.filter(Course.title.ilike(f"%{search}%"))
    total=q.count()
    courses=q.order_by(Course.enrolled_count.desc()).offset((page-1)*limit).limit(limit).all()
    return {"total":total,"page":page,"limit":limit,"pages":(total+limit-1)//limit,
            "courses":[_course(c,user,db) for c in courses]}

@router.get("/admin/all")
def admin_list(db=Depends(get_db), admin=Depends(get_current_admin)):
    return [_course(c) for c in db.query(Course).order_by(Course.created_at.desc()).all()]

@router.get("/id/{course_id}")
def get_course_by_id(course_id: int, db=Depends(get_db), user=Depends(get_optional_user)):
    c=db.query(Course).filter(Course.id==course_id,Course.status=="published").first()
    if not c: raise HTTPException(404,"Not found")
    return _course(c,user,db)

@router.get("/{slug}")
def get_course(slug: str, db=Depends(get_db), user=Depends(get_optional_user)):
    c=db.query(Course).filter(Course.slug==slug).first()
    if not c: raise HTTPException(404,"Not found")
    data=_course(c,user,db)
    enrolled=data["enrolled"]
    lessons=[]
    for l in c.lessons:
        if not l.is_published: continue
        ld={"id":l.id,"title":l.title,"description":l.description,
            "lesson_type":l.lesson_type,"duration":l.duration,
            "sort_order":l.sort_order,"is_free":l.is_free,
            "locked":not(l.is_free or enrolled or c.is_free)}
        if l.is_free or enrolled or c.is_free:
            ld["content"]=l.content; ld["video_url"]=l.video_url
            ld["video_type"]=l.video_type; ld["file_url"]=l.file_url
        lessons.append(ld)
    data["lessons"]=lessons
    return data

@router.post("/admin/create")
def create_course(req: CourseCreate, db=Depends(get_db), admin=Depends(get_current_admin)):
    slug=slugify(req.title); base=slug; i=1
    while db.query(Course).filter(Course.slug==slug).first():
        slug=f"{base}-{i}"; i+=1
    c=Course(title=req.title,slug=slug,description=req.description,
             short_desc=req.short_desc,thumbnail=req.thumbnail,
             level=req.level,language=req.language,status=req.status,
             is_free=req.is_free,price=req.price,discount_price=req.discount_price,
             category_id=req.category_id,instructor_id=admin.id,
             what_you_learn=req.what_you_learn,requirements=req.requirements,tags=req.tags)
    db.add(c); db.commit(); db.refresh(c)
    return _course(c)

@router.put("/admin/{course_id}")
def update_course(course_id: int, req: CourseUpdate, db=Depends(get_db), admin=Depends(get_current_admin)):
    c=db.query(Course).filter(Course.id==course_id).first()
    if not c: raise HTTPException(404,"Not found")
    for k,v in req.dict(exclude_unset=True).items():
        if k=="title" and v: c.slug=slugify(v)
        setattr(c,k,v)
    db.commit(); db.refresh(c)
    return _course(c)

@router.delete("/admin/{course_id}")
def delete_course(course_id: int, db=Depends(get_db), admin=Depends(get_current_admin)):
    c=db.query(Course).filter(Course.id==course_id).first()
    if not c: raise HTTPException(404,"Not found")
    db.delete(c); db.commit()
    return {"message":"Deleted"}

@router.post("/{course_id}/enroll")
def enroll(course_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    c=db.query(Course).filter(Course.id==course_id,Course.status=="published").first()
    if not c: raise HTTPException(404,"Not found")
    existing=db.query(Enrollment).filter(Enrollment.user_id==user.id,Enrollment.course_id==course_id).first()
    if existing: return {"message":"Already enrolled","enrollment_id":existing.id}
    if not c.is_free and c.price>0:
        from models.models import Payment
        paid=db.query(Payment).filter(Payment.user_id==user.id,Payment.course_id==course_id,Payment.status=="completed").first()
        if not paid: raise HTTPException(402,"Payment required")
    enr=Enrollment(user_id=user.id,course_id=course_id)
    db.add(enr); c.enrolled_count+=1; db.commit(); db.refresh(enr)
    return {"message":"Enrolled successfully","enrollment_id":enr.id}

@router.post("/{course_id}/progress/{lesson_id}")
def mark_complete(course_id: int, lesson_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    enr=db.query(Enrollment).filter(Enrollment.user_id==user.id,Enrollment.course_id==course_id).first()
    if not enr: raise HTTPException(403,"Not enrolled")
    prog=db.query(LessonProgress).filter(LessonProgress.user_id==user.id,LessonProgress.lesson_id==lesson_id).first()
    if not prog:
        prog=LessonProgress(user_id=user.id,lesson_id=lesson_id,completed=True,completed_at=datetime.utcnow())
        db.add(prog)
    else:
        prog.completed=True; prog.completed_at=datetime.utcnow()
    c=db.query(Course).filter(Course.id==course_id).first()
    total=c.total_lessons or 1
    done=db.query(LessonProgress).join(Lesson).filter(
        LessonProgress.user_id==user.id,Lesson.course_id==course_id,LessonProgress.completed==True).count()
    enr.progress=round((done/total)*100,1); enr.last_lesson_id=lesson_id
    if enr.progress>=100 and not enr.completed:
        enr.completed=True; enr.completed_at=datetime.utcnow(); user.xp_points+=100
    user.xp_points+=5; _update_level(user); db.commit()
    return {"progress":enr.progress,"completed":enr.completed,"xp_earned":5}

@router.post("/{course_id}/review")
def add_review(course_id: int, req: ReviewCreate, db=Depends(get_db), user=Depends(get_current_user)):
    if req.rating<1 or req.rating>5: raise HTTPException(400,"Rating 1-5")
    existing=db.query(CourseReview).filter(CourseReview.user_id==user.id,CourseReview.course_id==course_id).first()
    if existing: existing.rating=req.rating; existing.comment=req.comment
    else:
        db.add(CourseReview(user_id=user.id,course_id=course_id,rating=req.rating,comment=req.comment))
    c=db.query(Course).filter(Course.id==course_id).first()
    if c:
        reviews=db.query(CourseReview).filter(CourseReview.course_id==course_id).all()
        c.rating_avg=round(sum(r.rating for r in reviews)/len(reviews),1)
        c.rating_count=len(reviews)
    db.commit()
    return {"message":"Review submitted"}
