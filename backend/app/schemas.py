# backend/app/schemas.py
from pydantic import BaseModel, confloat, validator
from typing import Optional

class CalcRequest(BaseModel):
    height: confloat(gt=0)
    weight: confloat(gt=0)
    unit: Optional[str] = "metric"

    @validator("unit")
    def unit_check(cls, v):
        if v not in ("metric", "imperial"):
            raise ValueError("unit must be 'metric' or 'imperial'")
        return v

class CalcResponse(BaseModel):
    bmi: float
    category: str
    healthy_range: str
