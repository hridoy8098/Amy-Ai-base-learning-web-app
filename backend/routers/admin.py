from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from core.database import get_db
from core.security import get_current_admin
from models.models import (User, Course, Enrollment, Payment,
                                    QuizResult, AmyMessage, Badge,
                                    UserBadge, Notification, Coupon)
from datetime import datetime

router = APIRouter()

@router.get("/stats")
def stats(db=Depends(get_db), admin=Depends(get_current_admin)):
    revenue=sum(p.amount for p in db.query(Payment).filter(Payment.status=="completed").all())
    return {
        "users":       {"total":db.query(User).count(),"active":db.query(User).filter(User.is_active==True).count(),
                        "paid":db.query(User).filter(User.subscription_plan.in_(["basic","pro","premium"])).count()},
        "courses":     {"total":db.query(Course).count(),"published":db.query(Course).filter(Course.status=="published").count()},
        "enrollments": {"total":db.query(Enrollment).count(),"completed":db.query(Enrollment).filter(Enrollment.completed==True).count()},
        "payments":    {"count":db.query(Payment).filter(Payment.status=="completed").count(),"revenue":round(revenue,2)},
        "amy_messages":db.query(AmyMessage).count(),
        "quizzes":     db.query(QuizResult).count(),
    }

@router.get("/users")
def list_users(page: int=Query(1,ge=1), limit: int=Query(20,ge=1,le=100),
               search: Optional[str]=None, role: Optional[str]=None,
               db=Depends(get_db), admin=Depends(get_current_admin)):
    q=db.query(User)
    if search: q=q.filter(User.name.ilike(f"%{search}%")|User.email.ilike(f"%{search}%"))
    if role:   q=q.filter(User.role==role)
    total=q.count()
    users=q.order_by(User.created_at.desc()).offset((page-1)*limit).limit(limit).all()
    return {"total":total,"page":page,"limit":limit,"users":[{
        "id":u.id,"name":u.name,"email":u.email,"role":u.role,
        "is_active":u.is_active,"subscription_plan":u.subscription_plan,
        "xp_points":u.xp_points,"level":u.level,
        "created_at":u.created_at.isoformat() if u.created_at else None,
    } for u in users]}

class UserUpdate(BaseModel):
    role: Optional[str]=None; is_active: Optional[bool]=None
    subscription_plan: Optional[str]=None; subscription_expires: Optional[str]=None

@router.put("/users/{uid}")
def update_user(uid: int, req: UserUpdate, db=Depends(get_db), admin=Depends(get_current_admin)):
    u=db.query(User).filter(User.id==uid).first()
    if not u: raise HTTPException(404,"Not found")
    if req.role is not None:        u.role=req.role
    if req.is_active is not None:   u.is_active=req.is_active
    if req.subscription_plan:       u.subscription_plan=req.subscription_plan
    if req.subscription_expires:    u.subscription_expires=datetime.fromisoformat(req.subscription_expires)
    db.commit()
    return {"message":"Updated"}

@router.delete("/users/{uid}")
def delete_user(uid: int, db=Depends(get_db), admin=Depends(get_current_admin)):
    u=db.query(User).filter(User.id==uid).first()
    if not u: raise HTTPException(404,"Not found")
    if u.role=="superadmin": raise HTTPException(403,"Cannot delete superadmin")
    db.delete(u); db.commit()
    return {"message":"Deleted"}

@router.get("/payments")
def list_payments(page: int=Query(1,ge=1), limit: int=Query(20,ge=1,le=100),
                  status: Optional[str]=None, db=Depends(get_db), admin=Depends(get_current_admin)):
    q=db.query(Payment)
    if status: q=q.filter(Payment.status==status)
    total=q.count()
    ps=q.order_by(Payment.created_at.desc()).offset((page-1)*limit).limit(limit).all()
    return {"total":total,"page":page,"payments":[{
        "id":p.id,"user_id":p.user_id,"user_name":p.user.name if p.user else None,
        "course_id":p.course_id,"amount":p.amount,"method":p.method,
        "status":p.status,"transaction_id":p.transaction_id,"payment_type":p.payment_type,
        "created_at":p.created_at.isoformat() if p.created_at else None,
    } for p in ps]}

class PaymentUpdate(BaseModel):
    status: str; notes: Optional[str]=None

@router.put("/payments/{pid}")
def update_payment(pid: int, req: PaymentUpdate, db=Depends(get_db), admin=Depends(get_current_admin)):
    p=db.query(Payment).filter(Payment.id==pid).first()
    if not p: raise HTTPException(404,"Not found")
    old=p.status; p.status=req.status
    if req.notes: p.notes=req.notes
    if req.status=="completed" and old!="completed":
        if p.payment_type=="course" and p.course_id:
            if not db.query(Enrollment).filter(Enrollment.user_id==p.user_id,Enrollment.course_id==p.course_id).first():
                db.add(Enrollment(user_id=p.user_id,course_id=p.course_id))
                c=db.query(Course).filter(Course.id==p.course_id).first()
                if c: c.enrolled_count+=1
        elif p.payment_type=="subscription" and p.plan:
            u=db.query(User).filter(User.id==p.user_id).first()
            if u:
                u.subscription_plan=p.plan
                from datetime import timedelta
                u.subscription_expires=datetime.utcnow()+timedelta(days=30)
    db.commit()
    return {"message":"Updated"}

class BadgeCreate(BaseModel):
    name: str; description: Optional[str]=None
    icon: Optional[str]=None; condition: str; xp_reward: int=0

@router.get("/badges")
def list_badges(db=Depends(get_db), admin=Depends(get_current_admin)):
    return [{"id":b.id,"name":b.name,"icon":b.icon,"condition":b.condition,"xp_reward":b.xp_reward}
            for b in db.query(Badge).all()]

@router.post("/badges")
def create_badge(req: BadgeCreate, db=Depends(get_db), admin=Depends(get_current_admin)):
    b=Badge(**req.dict()); db.add(b); db.commit(); db.refresh(b)
    return {"id":b.id,"name":b.name}

@router.post("/badges/{bid}/award/{uid}")
def award_badge(bid: int, uid: int, db=Depends(get_db), admin=Depends(get_current_admin)):
    if db.query(UserBadge).filter(UserBadge.user_id==uid,UserBadge.badge_id==bid).first():
        return {"message":"Already awarded"}
    b=db.query(Badge).filter(Badge.id==bid).first()
    u=db.query(User).filter(User.id==uid).first()
    if not b or not u: raise HTTPException(404,"Not found")
    db.add(UserBadge(user_id=uid,badge_id=bid))
    u.xp_points+=b.xp_reward
    db.add(Notification(user_id=uid,title="New Badge!",
        message=f"You earned the '{b.name}' badge! {b.icon or '🏅'}",type="success"))
    db.commit()
    return {"message":"Awarded"}

class NotifBroadcast(BaseModel):
    title: str; message: str; type: str="info"; user_ids: Optional[list]=None

@router.post("/notify")
def notify(req: NotifBroadcast, db=Depends(get_db), admin=Depends(get_current_admin)):
    users=db.query(User).filter(User.id.in_(req.user_ids)).all() if req.user_ids else \
          db.query(User).filter(User.is_active==True).all()
    for u in users:
        db.add(Notification(user_id=u.id,title=req.title,message=req.message,type=req.type))
    db.commit()
    return {"message":f"Sent to {len(users)} users"}

class CouponCreate(BaseModel):
    code: str; discount_pct: float=0.0; discount_amt: float=0.0
    max_uses: int=100; expires_at: Optional[str]=None

@router.get("/coupons")
def list_coupons(db=Depends(get_db), admin=Depends(get_current_admin)):
    return [{"id":c.id,"code":c.code,"discount_pct":c.discount_pct,"discount_amt":c.discount_amt,
             "max_uses":c.max_uses,"used_count":c.used_count,"is_active":c.is_active}
            for c in db.query(Coupon).order_by(Coupon.created_at.desc()).all()]

@router.post("/coupons")
def create_coupon(req: CouponCreate, db=Depends(get_db), admin=Depends(get_current_admin)):
    if db.query(Coupon).filter(Coupon.code==req.code.upper()).first():
        raise HTTPException(400,"Code exists")
    c=Coupon(code=req.code.upper(),discount_pct=req.discount_pct,
             discount_amt=req.discount_amt,max_uses=req.max_uses)
    if req.expires_at: c.expires_at=datetime.fromisoformat(req.expires_at)
    db.add(c); db.commit(); db.refresh(c)
    return {"id":c.id,"code":c.code}

@router.delete("/coupons/{cid}")
def delete_coupon(cid: int, db=Depends(get_db), admin=Depends(get_current_admin)):
    c=db.query(Coupon).filter(Coupon.id==cid).first()
    if not c: raise HTTPException(404,"Not found")
    db.delete(c); db.commit()
    return {"message":"Deleted"}
