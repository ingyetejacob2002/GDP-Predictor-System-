(function () {
  const gdpSlider = document.getElementById("gdpSlider");
  const eduSlider = document.getElementById("eduSlider");
  const urbanSlider = document.getElementById("urbanSlider");
  const gdpValue = document.getElementById("gdpValue");
  const eduValue = document.getElementById("eduValue");
  const urbanValue = document.getElementById("urbanValue");
  const countrySelect = document.getElementById("countrySelect");
  const resultValue = document.getElementById("resultValue");
  const percentileText = document.getElementById("percentileText");
  const rangeFill = document.getElementById("rangeFill");

  let debounceTimer = null;

  function updateLabels() {
    gdpValue.textContent = "$" + Number(gdpSlider.value).toLocaleString();
    eduValue.textContent = Number(eduSlider.value).toFixed(2);
    urbanValue.textContent = Number(urbanSlider.value).toFixed(1) + "%";
  }

  async function predict() {
    updateLabels();
    resultValue.classList.add("is-loading");

    try {
      const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          gdp: parseFloat(gdpSlider.value),
          education: parseFloat(eduSlider.value),
          urban: parseFloat(urbanSlider.value),
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        resultValue.textContent = "err";
        percentileText.textContent = data.error || "Something went wrong.";
        return;
      }
      resultValue.textContent = data.prediction.toFixed(2);
      const pct = Math.max(0, Math.min(100, data.percentile));
      rangeFill.style.left = pct + "%";
      percentileText.textContent =
        `Higher than ${pct}% of the ${data.n_countries} countries in the dataset.`;
    } catch (err) {
      resultValue.textContent = "err";
      percentileText.textContent = "Could not reach the prediction service.";
    }
  }

  function debouncedPredict() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(predict, 120);
  }

  [gdpSlider, eduSlider, urbanSlider].forEach((el) => {
    el.addEventListener("input", () => {
      updateLabels();
      debouncedPredict();
    });
  });

  countrySelect.addEventListener("change", () => {
    const opt = countrySelect.options[countrySelect.selectedIndex];
    if (!opt.value) return;
    gdpSlider.value = opt.dataset.gdp;
    eduSlider.value = opt.dataset.education;
    urbanSlider.value = opt.dataset.urban;
    updateLabels();
    debouncedPredict();
  });

  updateLabels();
  predict();
})();
