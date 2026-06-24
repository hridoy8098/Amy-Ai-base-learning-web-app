from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from core.database import get_db
from core.security import get_current_user
from models.models import (User, Notification, Note, Bookmark,
                                    UserBadge, Certificate, Enrollment, Course)
from datetime import datetime
import uuid, os

router = APIRouter()

# ── Notifications ─────────────────────────────────────────────────

@router.get("/notifications")
def get_notifs(user=Depends(get_current_user), db=Depends(get_db)):
    ns=db.query(Notification).filter(Notification.user_id==user.id).order_by(Notification.created_at.desc()).limit(30).all()
    return [{"id":n.id,"title":n.title,"message":n.message,"type":n.type,
             "is_read":n.is_read,"link":n.link,"created_at":n.created_at.isoformat()} for n in ns]

@router.post("/notifications/read-all")
def read_all(user=Depends(get_current_user), db=Depends(get_db)):
    db.query(Notification).filter(Notification.user_id==user.id,Notification.is_read==False).update({"is_read":True})
    db.commit()
    return {"message":"All read"}

@router.put("/notifications/{nid}/read")
def read_one(nid: int, user=Depends(get_current_user), db=Depends(get_db)):
    n=db.query(Notification).filter(Notification.id==nid,Notification.user_id==user.id).first()
    if n: n.is_read=True; db.commit()
    return {"message":"Read"}

# ── Notes ─────────────────────────────────────────────────────────

class NoteCreate(BaseModel):
    title: Optional[str]=None; content: str; lesson_id: Optional[int]=None

class NoteUpdate(BaseModel):
    title: Optional[str]=None; content: Optional[str]=None

@router.get("/notes")
def get_notes(user=Depends(get_current_user), db=Depends(get_db)):
    ns=db.query(Note).filter(Note.user_id==user.id).order_by(Note.updated_at.desc()).all()
    return [{"id":n.id,"title":n.title,"content":n.content,"lesson_id":n.lesson_id,
             "lesson_title":n.lesson.title if n.lesson else None,
             "created_at":n.created_at.isoformat(),"updated_at":n.updated_at.isoformat()} for n in ns]

@router.post("/notes")
def create_note(req: NoteCreate, user=Depends(get_current_user), db=Depends(get_db)):
    n=Note(user_id=user.id,title=req.title,content=req.content,lesson_id=req.lesson_id)
    db.add(n); db.commit(); db.refresh(n)
    return {"id":n.id,"message":"Saved"}

@router.put("/notes/{nid}")
def update_note(nid: int, req: NoteUpdate, user=Depends(get_current_user), db=Depends(get_db)):
    n=db.query(Note).filter(Note.id==nid,Note.user_id==user.id).first()
    if not n: raise HTTPException(404,"Not found")
    if req.title is not None: n.title=req.title
    if req.content is not None: n.content=req.content
    db.commit()
    return {"message":"Updated"}

@router.delete("/notes/{nid}")
def delete_note(nid: int, user=Depends(get_current_user), db=Depends(get_db)):
    n=db.query(Note).filter(Note.id==nid,Note.user_id==user.id).first()
    if not n: raise HTTPException(404,"Not found")
    db.delete(n); db.commit()
    return {"message":"Deleted"}

# ── Bookmarks ─────────────────────────────────────────────────────

class BmCreate(BaseModel):
    lesson_id: Optional[int]=None; course_id: Optional[int]=None

@router.get("/bookmarks")
def get_bookmarks(user=Depends(get_current_user), db=Depends(get_db)):
    bs=db.query(Bookmark).filter(Bookmark.user_id==user.id).order_by(Bookmark.created_at.desc()).all()
    return [{"id":b.id,"lesson_id":b.lesson_id,"lesson_title":b.lesson.title if b.lesson else None,
             "course_id":b.course_id,"created_at":b.created_at.isoformat()} for b in bs]

@router.post("/bookmarks")
def toggle_bookmark(req: BmCreate, user=Depends(get_current_user), db=Depends(get_db)):
    existing=db.query(Bookmark).filter(Bookmark.user_id==user.id,
        Bookmark.lesson_id==req.lesson_id,Bookmark.course_id==req.course_id).first()
    if existing: db.delete(existing); db.commit(); return {"message":"Removed","bookmarked":False}
    db.add(Bookmark(user_id=user.id,lesson_id=req.lesson_id,course_id=req.course_id))
    db.commit()
    return {"message":"Bookmarked","bookmarked":True}

# ── Badges ────────────────────────────────────────────────────────

@router.get("/badges")
def get_badges(user=Depends(get_current_user), db=Depends(get_db)):
    ubs=db.query(UserBadge).filter(UserBadge.user_id==user.id).all()
    return [{"id":ub.badge.id,"name":ub.badge.name,"description":ub.badge.description,
             "icon":ub.badge.icon,"earned_at":ub.earned_at.isoformat()} for ub in ubs]

# ── Certificates ──────────────────────────────────────────────────

@router.get("/certificates")
def get_certs(user=Depends(get_current_user), db=Depends(get_db)):
    cs=db.query(Certificate).filter(Certificate.user_id==user.id).all()
    return [{"id":c.id,"course_title":c.course.title if c.course else None,
             "cert_code":c.cert_code,"issued_at":c.issued_at.isoformat(),
             "file_path":c.file_path} for c in cs]

@router.post("/certificates/generate/{course_id}")
def generate_cert(course_id: int, user=Depends(get_current_user), db=Depends(get_db)):
    enr=db.query(Enrollment).filter(Enrollment.user_id==user.id,
        Enrollment.course_id==course_id,Enrollment.completed==True).first()
    if not enr: raise HTTPException(403,"Course not completed")
    existing=db.query(Certificate).filter(Certificate.user_id==user.id,Certificate.course_id==course_id).first()
    if existing: return {"cert_code":existing.cert_code,"file_path":existing.file_path}
    course=db.query(Course).filter(Course.id==course_id).first()
    cert_code=f"AMY-{uuid.uuid4().hex[:10].upper()}"
    cert_html=f"""<html><body style="font-family:Arial;text-align:center;padding:60px">
<h1 style="color:#7b6ef6">Certificate of Completion</h1>
<h2>This certifies that</h2><h1>{user.name}</h1>
<p>has successfully completed</p>
<h2 style="color:#7b6ef6">{course.title}</h2>
<p>Code: <strong>{cert_code}</strong></p>
<p>Issued: {datetime.utcnow().strftime('%B %d, %Y')}</p>
<p style="color:#999">Amy Learning Platform</p>
</body></html>"""
    cert_dir=os.path.join("uploads","certificates")
    os.makedirs(cert_dir,exist_ok=True)
    with open(os.path.join(cert_dir,f"{cert_code}.html"),"w",encoding="utf-8") as f:
        f.write(cert_html)
    c=Certificate(user_id=user.id,course_id=course_id,cert_code=cert_code,
                  file_path=f"/uploads/certificates/{cert_code}.html")
    db.add(c); db.commit()
    return {"cert_code":cert_code,"file_path":c.file_path,"message":"Generated"}

# ── Leaderboard ───────────────────────────────────────────────────

@router.get("/leaderboard")
def leaderboard(limit: int = Query(20, ge=1, le=100), db=Depends(get_db)):
    users=db.query(User).filter(User.is_active==True).order_by(
        User.xp_points.desc(),
        User.level.desc(),
        User.streak_days.desc(),
        User.name.asc(),
    ).limit(limit).all()
    return [{"rank":i+1,"name":u.name,"avatar":u.avatar,"xp":u.xp_points,
             "level":u.level,"streak":u.streak_days} for i,u in enumerate(users)]

# ── My Courses ────────────────────────────────────────────────────

@router.get("/my-courses")
def my_courses(user=Depends(get_current_user), db=Depends(get_db)):
    enrs=db.query(Enrollment).filter(Enrollment.user_id==user.id).all()
    return [{"course_id":e.course.id,"title":e.course.title,"slug":e.course.slug,
             "thumbnail":e.course.thumbnail,"progress":e.progress,"completed":e.completed,
             "enrolled_at":e.enrolled_at.isoformat() if e.enrolled_at else None,
             "completed_at":e.completed_at.isoformat() if e.completed_at else None}
            for e in enrs if e.course]
