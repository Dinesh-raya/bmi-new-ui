# backend/app/main.py
import os
from fastapi import FastAPI, HTTPException, Depends
from .schemas import CalcRequest, CalcResponse
from .database import SessionLocal, init_db
from .crud import save_calculation, get_history
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

SAVE_HISTORY = os.getenv("SAVE_HISTORY", "false").lower() == "true"

app = FastAPI(title="BMI Calculator API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lock down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def calc_bmi(height: float, weight: float, unit: str):
    if unit == "imperial":
        # height in inches, weight in pounds
        bmi = (weight / (height * height)) * 703
    else:
        # metric: height in cm -> meters
        h_m = height / 100.0
        bmi = weight / (h_m * h_m)
    return round(bmi, 2)

def classify_bmi(bmi: float):
    if bmi < 18.5:
        return "Underweight", "Below 18.5"
    if bmi < 25:
        return "Normal", "18.5 - 24.9"
    if bmi < 30:
        return "Overweight", "25 - 29.9"
    return "Obese", "30+"

@app.on_event("startup")
def startup():
    init_db()

@app.post("/api/calculate", response_model=CalcResponse)
def calculate(req: CalcRequest, db: Session = Depends(get_db)):
    try:
        bmi = calc_bmi(req.height, req.weight, req.unit)
        category, healthy = classify_bmi(bmi)
        if SAVE_HISTORY:
            save_calculation(db, req.height, req.weight, req.unit, bmi, category)
        return {"bmi": bmi, "category": category, "healthy_range": healthy}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/history")
def history(db: Session = Depends(get_db)):
    return get_history(db)
