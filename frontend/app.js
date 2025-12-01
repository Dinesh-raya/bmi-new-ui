const API = "https://bmi-new-ui.onrender.com";

const unitSelect = document.getElementById("unit");
const heightMetric = document.getElementById("height-metric");
const heightImperial = document.getElementById("height-imperial");

unitSelect.addEventListener("change", () => {
  if(unitSelect.value === "metric") {
    heightMetric.classList.remove("hidden");
    heightImperial.classList.add("hidden");
  } else {
    heightMetric.classList.add("hidden");
    heightImperial.classList.remove("hidden");
  }
});

document.getElementById("calcBtn").addEventListener("click", async () => {
  const unit = unitSelect.value;
  let height, weight;

  weight = parseFloat(document.getElementById("weight").value);
  if (!weight || weight <= 0) return alert("Enter valid weight");

  if(unit === "metric") {
    height = parseFloat(document.getElementById("height-cm").value);
    if (!height || height <= 0) return alert("Enter valid height in cm");
  } else {
    const ft = parseFloat(document.getElementById("height-ft").value);
    const inch = parseFloat(document.getElementById("height-in").value);
    if(ft < 0 || inch < 0) return alert("Enter valid height in ft/in");
    height = ft * 12 + inch; // total inches
  }

  try {
    const res = await fetch(`${API}/api/calculate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ height, weight, unit })
    });
    if(!res.ok) throw new Error(await res.text());
    const data = await res.json();

    document.getElementById("bmiVal").textContent = data.bmi;
    document.getElementById("category").textContent = data.category;
    document.getElementById("range").textContent = data.healthy_range;
    document.getElementById("result").classList.remove("hidden");

    addHistory(data.bmi, data.category);
  } catch(e) {
    alert("Error: " + e.message);
  }
});

// Minimal BMI history chart
const history = [];
function addHistory(bmi, category) {
  history.push({bmi, category});
  const chart = document.getElementById("historyChart");
  if(!chart) {
    const div = document.createElement("div");
    div.id = "historyChart";
    div.className = "mt-4 p-4 bg-gray-100 rounded";
    document.querySelector("body > div").appendChild(div);
  }
  document.getElementById("historyChart").innerHTML = history
    .map((h,i)=>`#${i+1}: BMI=${h.bmi}, ${h.category}`).join("<br>");
}
