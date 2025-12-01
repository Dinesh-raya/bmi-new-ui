# backend/app/tests/test_bmi.py
from app.main import calc_bmi, classify_bmi

def test_metric_bmi():
    bmi = calc_bmi(170, 65, "metric")
    assert round(bmi,2) == 22.49

def test_imperial_bmi():
    bmi = calc_bmi(70, 154, "imperial")
    assert round(bmi, 2) == round((154/(70*70))*703, 2)

def test_classify():
    assert classify_bmi(22.0)[0] == "Normal"
    assert classify_bmi(17.0)[0] == "Underweight"
