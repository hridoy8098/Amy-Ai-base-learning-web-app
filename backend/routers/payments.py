from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from core.database import get_db
from core.security import get_current_user
from models.models import Payment, Course, Enrollment, Coupon, User, Notification
from datetime import datetime

router = APIRouter()

PLANS = {
    "basic":   {"price":199,  "label":"Basic Plan"},
    "pro":     {"price":399,  "label":"Pro Plan"},
    "premium": {"price":999,  "label":"Premium Plan"},
}

class InitiateRequest(BaseModel):
    payment_type: str; course_id: Optional[int]=None
    plan: Optional[str]=None; method: str; coupon_code: Optional[str]=None

class ConfirmRequest(BaseModel):
    payment_id: int; transaction_id: str

class CouponCheck(BaseModel):
    code: str; course_id: Optional[int]=None; plan: Optional[str]=None

@router.post("/initiate")
def initiate(req: InitiateRequest, user=Depends(get_current_user), db=Depends(get_db)):
    amount=0.0
    if req.payment_type=="course":
        if not req.course_id: raise HTTPException(400,"course_id required")
        c=db.query(Course).filter(Course.id==req.course_id).first()
        if not c: raise HTTPException(404,"Course not found")
        if c.is_free: raise HTTPException(400,"Course is free")
        if db.query(Enrollment).filter(Enrollment.user_id==user.id,Enrollment.course_id==req.course_id).first():
            raise HTTPException(400,"Already enrolled")
        amount=c.discount_price if c.discount_price else c.price
    elif req.payment_type=="subscription":
        if not req.plan or req.plan not in PLANS: raise HTTPException(400,"Invalid plan")
        amount=PLANS[req.plan]["price"]
    else:
        raise HTTPException(400,"Invalid payment_type")

    coupon=None
    if req.coupon_code:
        coupon=db.query(Coupon).filter(Coupon.code==req.coupon_code.upper(),Coupon.is_active==True).first()
        if not coupon: raise HTTPException(400,"Invalid coupon")
        if coupon.expires_at and coupon.expires_at<datetime.utcnow(): raise HTTPException(400,"Coupon expired")
        if coupon.used_count>=coupon.max_uses: raise HTTPException(400,"Coupon limit reached")
        if coupon.discount_pct>0: amount=round(amount*(1-coupon.discount_pct/100),2)
        elif coupon.discount_amt>0: amount=max(0,amount-coupon.discount_amt)

    p=Payment(user_id=user.id,course_id=req.course_id,amount=amount,
              method=req.method,status="pending",payment_type=req.payment_type,plan=req.plan)
    db.add(p)
    if coupon: coupon.used_count+=1
    db.commit(); db.refresh(p)

    instructions={}
    if req.method=="bkash":
        instructions={"method":"bkash","merchant_number":"01XXXXXXXXX","amount":amount,
                      "reference":f"AMY-{p.id}","instructions":f"Send {amount} BDT to 01XXXXXXXXX via bKash. Reference: AMY-{p.id}"}
    elif req.method=="nagad":
        instructions={"method":"nagad","merchant_number":"01XXXXXXXXX","amount":amount,
                      "reference":f"AMY-{p.id}","instructions":f"Send {amount} BDT to 01XXXXXXXXX via Nagad. Reference: AMY-{p.id}"}

    return {"payment_id":p.id,"amount":amount,"status":"pending","instructions":instructions,
            "message":"Complete payment and submit your transaction ID"}

@router.post("/confirm")
def confirm(req: ConfirmRequest, user=Depends(get_current_user), db=Depends(get_db)):
    p=db.query(Payment).filter(Payment.id==req.payment_id,Payment.user_id==user.id).first()
    if not p: raise HTTPException(404,"Not found")
    if p.status=="completed": return {"message":"Already confirmed"}
    p.transaction_id=req.transaction_id
    db.add(Notification(user_id=user.id,title="Payment Submitted",
        message=f"Payment of {p.amount} BDT submitted. We'll verify within 24 hours.",type="info"))
    db.commit()
    return {"message":"Submitted for verification","payment_id":p.id}

@router.post("/coupon/check")
def check_coupon(req: CouponCheck, user=Depends(get_current_user), db=Depends(get_db)):
    c=db.query(Coupon).filter(Coupon.code==req.code.upper(),Coupon.is_active==True).first()
    if not c: raise HTTPException(400,"Invalid coupon")
    if c.expires_at and c.expires_at<datetime.utcnow(): raise HTTPException(400,"Expired")
    if c.used_count>=c.max_uses: raise HTTPException(400,"Limit reached")
    return {"valid":True,"code":c.code,"discount_pct":c.discount_pct,"discount_amt":c.discount_amt}

@router.get("/history")
def history(user=Depends(get_current_user), db=Depends(get_db)):
    ps=db.query(Payment).filter(Payment.user_id==user.id).order_by(Payment.created_at.desc()).all()
    return [{"id":p.id,"amount":p.amount,"method":p.method,"status":p.status,
             "payment_type":p.payment_type,"plan":p.plan,"transaction_id":p.transaction_id,
             "created_at":p.created_at.isoformat() if p.created_at else None} for p in ps]

@router.get("/plans")
def get_plans():
    return [
        {"id":"free","name":"Free","price":0,"features":["10 Amy messages/day","5 voice messages/day","3 quiz/day","Free learning tools"]},
        {"id":"basic","name":"Basic","price":199,"currency":"BDT","period":"month","features":["Unlimited Amy messages","20 voice/day","10 quiz/day","Certificates","Paid courses purchased separately"]},
        {"id":"pro","name":"Pro","price":399,"currency":"BDT","period":"month","popular":True,"features":["Everything unlimited","Priority AI","Advanced analytics","Certificates","Paid courses purchased separately"]},
        {"id":"premium","name":"Premium","price":999,"currency":"BDT","period":"month","features":["Everything in Pro","Custom learning path","Early access","Priority support","Paid courses purchased separately"]},
    ]
