const API = "https://bmi-new-ui.onrender.com";

// Elements

const unitSelect = document.getElementById("unit");
const heightMetric = document.getElementById("height-metric");
const heightImperial = document.getElementById("height-imperial");
const errorEl = document.getElementById("error");

// Toggle inputs for metric/imperial
unitSelect.addEventListener("change", () => {
  if(unitSelect.value === "metric") {
    heightMetric.classList.remove("hidden");
    heightImperial.classList.add("hidden");
  } else {
    heightMetric.classList.add("hidden");
    heightImperial.classList.remove("hidden");
  }
});

// BMI history (frontend only)
const history = [];
function addHistory(bmi, category) {
  history.push({bmi, category});
  let chart = document.getElementById("historyChart");
  if(!chart){
    chart = document.createElement("div");
    chart.id = "historyChart";
    chart.className = "mt-4 p-4 bg-gray-100 rounded";
    document.querySelector("body > div").appendChild(chart);
  }
  chart.innerHTML = history.map((h,i)=>`#${i+1}: BMI=${h.bmi}, ${h.category}`).join("<br>");
}

// Calculate button click
document.getElementById("calcBtn").addEventListener("click", async () => {
  errorEl.textContent = "";
  const unit = unitSelect.value;
  let height, weight;

  weight = parseFloat(document.getElementById("weight").value);
  if(!weight || weight <= 0){
    errorEl.textContent = "Enter valid weight";
    return;
  }

  if(unit === "metric"){
    height = parseFloat(document.getElementById("height-cm").value);
    if(!height || height <= 0){
      errorEl.textContent = "Enter valid height in cm";
      return;
    }
  } else {
    const ft = parseFloat(document.getElementById("height-ft").value);
    const inch = parseFloat(document.getElementById("height-in").value);
    if(ft < 0 || inch < 0){
      errorEl.textContent = "Enter valid height in ft/in";
      return;
    }
    height = ft * 12 + inch; // total inches for backend
  }

  try {
    const res = await fetch(`${API}/api/calculate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ height, weight, unit })
    });
    if(!res.ok) throw new Error(await res.text());
    const data = await res.json();

    const bmiEl = document.getElementById("bmiVal");
    const catEl = document.getElementById("category");
    const rangeEl = document.getElementById("range");
    const resultEl = document.getElementById("result");

    if(bmiEl && catEl && rangeEl && resultEl){
      bmiEl.textContent = data.bmi;
      catEl.textContent = data.category;
      rangeEl.textContent = data.healthy_range;
      resultEl.classList.remove("hidden");
    }

    addHistory(data.bmi, data.category);

  } catch(e) {
    errorEl.textContent = "Error: " + e.message;
  }
});
const dob = document.getElementById("dob").value;
const gender = document.getElementById("gender").value;

const res = await fetch(`${API}/api/calculate`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    height,
    weight,
    unit,
    dob,
    gender
  })
});
const data = await res.json();

// Update UI
document.getElementById("bmiVal").textContent = data.bmi;
document.getElementById("suggestedBMI").textContent = `Suggested BMI: ${data.suggested_bmi_min} - ${data.suggested_bmi_max}`;
document.getElementById("suggestedWeight").textContent = `Suggested weight: ${data.suggested_weight_min} - ${data.suggested_weight_max} kg`;
document.getElementById("bmiStatus").textContent = `Status: ${data.status}`;


