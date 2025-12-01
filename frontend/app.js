const API = "https://bmi-new-ui.onrender.com"; // replace with your backend URL

const unitSelect = document.getElementById("unit");
const heightMetric = document.getElementById("height-metric");
const heightImperial = document.getElementById("height-imperial");
const calcBtn = document.getElementById("calcBtn");
const dobEl = document.getElementById("dob");
const genderEl = document.getElementById("gender");
const bmiChartCtx = document.getElementById("bmiChart").getContext("2d");
let bmiChart;

unitSelect.addEventListener("change", () => {
  if (unitSelect.value === "metric") {
    heightMetric.classList.remove("hidden");
    heightImperial.classList.add("hidden");
  } else {
    heightMetric.classList.add("hidden");
    heightImperial.classList.remove("hidden");
  }
});

async function fetchHistory() {
  try {
    const res = await fetch(`${API}/api/history`);
    const data = await res.json();
    if (!Array.isArray(data)) return;

    const labels = data.map((e, i) => `#${i + 1} (${new Date(e.created_at).toLocaleDateString()})`);
    const bmiData = data.map(e => e.bmi);

    if (bmiChart) bmiChart.destroy();
    bmiChart = new Chart(bmiChartCtx, {
      type: 'line',
      data: { labels, datasets: [{ label: 'BMI Trend', data: bmiData, borderColor: 'blue', backgroundColor: 'rgba(0,0,255,0.1)', fill: true, tension: 0.3 }] },
      options: { responsive: true, plugins: { legend: { display: true } } }
    });
  } catch (e) { console.log(e); }
}

function showAdvice(status) {
  const adviceEl = document.getElementById("advice");
  const messages = {
    underweight: "Increase calories & protein intake.",
    normal: "Maintain a healthy lifestyle.",
    overweight: "Increase cardio & monitor diet."
  };
  adviceEl.textContent = messages[status] || "";
  adviceEl.classList.remove("hidden");
}

calcBtn.addEventListener("click", async () => {
  const unit = unitSelect.value;
  let height, weight;

  weight = parseFloat(document.getElementById("weight").value);
  if (!weight || weight <= 0) { alert("Enter valid weight"); return; }

  if (unit === "metric") {
    height = parseFloat(document.getElementById("height-cm").value);
    if (!height || height <= 0) { alert("Enter valid height"); return; }
    height = height / 100; // convert cm to meters
  } else {
    const ft = parseFloat(document.getElementById("height-ft").value);
    const inch = parseFloat(document.getElementById("height-in").value);
    if (ft < 0 || inch < 0) { alert("Enter valid height"); return; }
    height = ft * 12 + inch; // inches
  }

  const dob = dobEl.value;
  const gender = genderEl.value;
  if (!dob || !gender) { alert("Enter DOB and select gender"); return; }

  try {
    const res = await fetch(`${API}/api/calculate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ height, weight, unit, dob, gender })
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();

    document.getElementById("bmiVal").textContent = data.bmi;
    document.getElementById("suggestedBMI").textContent = `Suggested BMI: ${data.suggested_bmi_min} - ${data.suggested_bmi_max}`;
    document.getElementById("suggestedWeight").textContent = `Suggested weight: ${data.suggested_weight_min} - ${data.suggested_weight_max} kg`;
    document.getElementById("bmiStatus").textContent = `Status: ${data.status}`;
    document.getElementById("result").classList.remove("hidden");

    showAdvice(data.status);
    fetchHistory();
  } catch (e) { alert("Error: " + e.message); }
});

fetchHistory();
