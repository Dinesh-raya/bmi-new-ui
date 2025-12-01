# backend/app/models.py
from sqlalchemy import Column, Integer, Float, String, DateTime
from .database import Base
from datetime import datetime

class Calculation(Base):
    __tablename__ = "calculations"
    id = Column(Integer, primary_key=True, index=True)
    height = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    unit = Column(String(10), default="metric")
    bmi = Column(Float, nullable=False)
    category = Column(String(30), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
