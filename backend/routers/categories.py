from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from core.database import get_db
from core.security import get_current_admin
from models.models import Category
import re

router = APIRouter()

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]','',text)
    text = re.sub(r'[\s_-]+','-',text)
    return text

class CatCreate(BaseModel):
    name: str; description: Optional[str]=None
    icon: Optional[str]=None; color: Optional[str]=None; sort_order: int=0

class CatUpdate(BaseModel):
    name: Optional[str]=None; description: Optional[str]=None
    icon: Optional[str]=None; color: Optional[str]=None
    is_active: Optional[bool]=None; sort_order: Optional[int]=None

def _cat(c):
    return {"id":c.id,"name":c.name,"slug":c.slug,"description":c.description,
            "icon":c.icon,"color":c.color,"is_active":c.is_active,
            "sort_order":c.sort_order,"course_count":len(c.courses) if c.courses else 0}

@router.get("")
def list_categories(db=Depends(get_db)):
    return [_cat(c) for c in db.query(Category).filter(Category.is_active==True).order_by(Category.sort_order).all()]

@router.get("/all")
def list_all(db=Depends(get_db), admin=Depends(get_current_admin)):
    return [_cat(c) for c in db.query(Category).order_by(Category.sort_order).all()]

@router.post("")
def create_cat(req: CatCreate, db=Depends(get_db), admin=Depends(get_current_admin)):
    slug = slugify(req.name); base=slug; i=1
    while db.query(Category).filter(Category.slug==slug).first():
        slug=f"{base}-{i}"; i+=1
    c = Category(name=req.name,slug=slug,description=req.description,icon=req.icon,color=req.color,sort_order=req.sort_order)
    db.add(c); db.commit(); db.refresh(c)
    return _cat(c)

@router.put("/{cat_id}")
def update_cat(cat_id: int, req: CatUpdate, db=Depends(get_db), admin=Depends(get_current_admin)):
    c = db.query(Category).filter(Category.id==cat_id).first()
    if not c: raise HTTPException(404,"Not found")
    for k,v in req.dict(exclude_unset=True).items():
        if k=="name" and v: c.slug=slugify(v)
        setattr(c,k,v)
    db.commit(); db.refresh(c)
    return _cat(c)

@router.delete("/{cat_id}")
def delete_cat(cat_id: int, db=Depends(get_db), admin=Depends(get_current_admin)):
    c = db.query(Category).filter(Category.id==cat_id).first()
    if not c: raise HTTPException(404,"Not found")
    db.delete(c); db.commit()
    return {"message":"Deleted"}
