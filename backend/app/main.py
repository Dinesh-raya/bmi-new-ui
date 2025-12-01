# backend/app/main.py
import os
from fastapi import FastAPI, HTTPException, Depends
from .schemas import CalcRequest, CalcResponse
from .database import SessionLocal, init_db
from .crud import save_calculation, get_history
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import datetime

suggested_bmi_ranges = {
    "male": { "5-10": (14.5, 19.5), "10-18": (16.5, 23.5), "18-24": (18.5, 24.9), "25-34": (19.0, 25.9),
              "35-44": (20.0, 26.9), "45-54": (21.0, 27.9), "55-64": (22.0, 28.9), "65+": (23.0, 29.9) },
    "female": { "5-10": (14.5, 19.5), "10-18": (16.5, 23.5), "18-24": (18.5, 24.9), "25-34": (19.0, 25.9),
                "35-44": (20.0, 26.9), "45-54": (21.0, 27.9), "55-64": (22.0, 28.9), "65+": (23.0, 29.9) },
}

def calculate_age(dob: str):
    birthdate = datetime.datetime.strptime(dob, "%Y-%m-%d").date()
    today = datetime.date.today()
    age_years = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age_years

def get_age_group(age):
    if 5 <= age < 10: return "5-10"
    elif 10 <= age < 18: return "10-18"
    elif 18 <= age < 25: return "18-24"
    elif 25 <= age < 35: return "25-34"
    elif 35 <= age < 45: return "35-44"
    elif 45 <= age < 55: return "45-54"
    elif 55 <= age < 65: return "55-64"
    else: return "65+"

# Inside your existing /calculate endpoint
age_years = calculate_age(data["dob"])
age_group = get_age_group(age_years)
gender = data.get("gender","male").lower()

suggested_range = suggested_bmi_ranges.get(gender, {}).get(age_group)
if suggested_range:
    suggested_bmi_min, suggested_bmi_max = suggested_range
    suggested_weight_min = round(suggested_bmi_min * height**2,2)
    suggested_weight_max = round(suggested_bmi_max * height**2,2)
else:
    suggested_bmi_min = suggested_bmi_max = suggested_weight_min = suggested_weight_max = None

# Determine status
if suggested_range:
    if bmi < suggested_bmi_min: status = "underweight"
    elif bmi > suggested_bmi_max: status = "overweight"
    else: status = "normal"
else:
    status = "unknown"

# Add these fields to your JSON response
return {
    "bmi": bmi,
    "age_years": age_years,
    "suggested_bmi_min": suggested_bmi_min,
    "suggested_bmi_max": suggested_bmi_max,
    "suggested_weight_min": suggested_weight_min,
    "suggested_weight_max": suggested_weight_max,
    "status": status
}


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
