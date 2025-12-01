from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import datetime

app = FastAPI()

# Allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with frontend URL if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory history storage
history = []

suggested_bmi_ranges = {
    "male": {
        "5-10": (14.5, 19.5),
        "10-18": (16.5, 23.5),
        "18-24": (18.5, 24.9),
        "25-34": (19.0, 25.9),
        "35-44": (20.0, 26.9),
        "45-54": (21.0, 27.9),
        "55-64": (22.0, 28.9),
        "65+": (23.0, 29.9),
    },
    "female": {
        "5-10": (14.5, 19.5),
        "10-18": (16.5, 23.5),
        "18-24": (18.5, 24.9),
        "25-34": (19.0, 25.9),
        "35-44": (20.0, 26.9),
        "45-54": (21.0, 27.9),
        "55-64": (22.0, 28.9),
        "65+": (23.0, 29.9),
    },
}

class BMIRequest(BaseModel):
    height: float
    weight: float
    unit: str
    dob: str
    gender: str

def calculate_bmi(height_meters, weight):
    return round(weight / (height_meters ** 2), 2)

def calculate_age(dob: str):
    birthdate = datetime.datetime.strptime(dob, "%Y-%m-%d").date()
    today = datetime.date.today()
    age_years = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age_years

def get_age_group(age):
    if 5 <= age < 10:
        return "5-10"
    elif 10 <= age < 18:
        return "10-18"
    elif 18 <= age < 25:
        return "18-24"
    elif 25 <= age < 35:
        return "25-34"
    elif 35 <= age < 45:
        return "35-44"
    elif 45 <= age < 55:
        return "45-54"
    elif 55 <= age < 65:
        return "55-64"
    else:
        return "65+"

@app.post("/api/calculate")
def calculate_bmi_endpoint(req: BMIRequest):
    # Convert height to meters if imperial
    height_meters = req.height
    if req.unit.lower() == "imperial":
        height_meters = ((req.height) * 0.0254)  # req.height should be in inches

    bmi = calculate_bmi(height_meters, req.weight)
    age_years = calculate_age(req.dob)
    age_group = get_age_group(age_years)
    gender = req.gender.lower()

    suggested_range = suggested_bmi_ranges.get(gender, {}).get(age_group, None)
    if suggested_range:
        suggested_bmi_min, suggested_bmi_max = suggested_range
        suggested_weight_min = round(suggested_bmi_min * (height_meters ** 2), 2)
        suggested_weight_max = round(suggested_bmi_max * (height_meters ** 2), 2)
    else:
        suggested_bmi_min = suggested_bmi_max = suggested_weight_min = suggested_weight_max = None

    # BMI status
    if suggested_range:
        if bmi < suggested_bmi_min:
            status = "underweight"
        elif bmi > suggested_bmi_max:
            status = "overweight"
        else:
            status = "normal"
    else:
        status = "unknown"

    # Save to history
    history.append({
        "bmi": bmi,
        "age": age_years,
        "gender": gender,
        "created_at": datetime.datetime.now().isoformat()
    })

    return {
        "bmi": bmi,
        "age_years": age_years,
        "suggested_bmi_min": suggested_bmi_min,
        "suggested_bmi_max": suggested_bmi_max,
        "suggested_weight_min": suggested_weight_min,
        "suggested_weight_max": suggested_weight_max,
        "status": status
    }

@app.get("/api/history")
def get_history():
    return history
