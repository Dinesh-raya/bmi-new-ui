# backend/app/crud.py
from sqlalchemy.orm import Session
from . import models
from datetime import datetime

def save_calculation(db: Session, height, weight, unit, bmi, category):
    calc = models.Calculation(height=height, weight=weight, unit=unit, bmi=bmi, category=category, created_at=datetime.utcnow())
    db.add(calc)
    db.commit()
    db.refresh(calc)
    return calc

def get_history(db: Session, limit: int = 50):
    return db.query(models.Calculation).order_by(models.Calculation.created_at.desc()).limit(limit).all()
