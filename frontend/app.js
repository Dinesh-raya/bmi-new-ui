// frontend/app.js
const API = (window.API_URL || "").replace(/\/$/, "") || "https://your-backend-url.com";

document.getElementById("calcBtn").addEventListener("click", async () => {
  const height = parseFloat(document.getElementById("height").value);
  const weight = parseFloat(document.getElementById("weight").value);
  const unit = document.getElementById("unit").value;
  const err = document.getElementById("error");
  err.textContent = "";

  if (!height || !weight) {
    err.textContent = "Provide valid height and weight.";
    return;
  }

  try {
    const res = await fetch(`${API}/api/calculate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ height, weight, unit })
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    document.getElementById("bmiVal").textContent = data.bmi;
    document.getElementById("category").textContent = data.category;
    document.getElementById("range").textContent = data.healthy_range;
    document.getElementById("result").classList.remove("hidden");
  } catch (e) {
    err.textContent = "Error: " + e.message;
  }
});
