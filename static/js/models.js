(function () {
  const DEEP_BLUE = "#06598a";
  const AMBER = "#e39a3c";
  const INK_SOFT = "#4a5568";
  const LINE = "#e3e7ec";
  const MIDNIGHT = "#17233f";

  // ---- Model comparison bar chart ----
  const sorted = [...MODEL_RESULTS].sort((a, b) => b.mae - a.mae); // worst first -> best at top
  const chartEl = document.getElementById("modelChart");
  if (chartEl) {
    new Chart(chartEl.getContext("2d"), {
      type: "bar",
      data: {
        labels: sorted.map((m) => m.name),
        datasets: [
          {
            data: sorted.map((m) => m.mae),
            backgroundColor: sorted.map((m) => (FINAL_MODEL_NAME.includes(m.name) ? AMBER : DEEP_BLUE)),
            borderRadius: 5,
            barThickness: 22,
          },
        ],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: MIDNIGHT,
            titleFont: { family: "IBM Plex Mono" },
            bodyFont: { family: "IBM Plex Mono" },
            callbacks: { label: (item) => `MAE: ${item.parsed.x.toFixed(3)}` },
          },
        },
        scales: {
          x: {
            title: { display: true, text: "LOOCV MAE (percentage points)", color: INK_SOFT, font: { family: "IBM Plex Sans", size: 11 } },
            grid: { color: LINE },
            ticks: { color: INK_SOFT, font: { family: "IBM Plex Mono", size: 10 } },
          },
          y: {
            grid: { display: false },
            ticks: { color: "#12181f", font: { family: "IBM Plex Sans", size: 12, weight: "600" } },
          },
        },
      },
    });
  }

  // ---- Predicted vs Actual ----
  const paEl = document.getElementById("predActualChart");
  if (paEl) {
    const vals = PRED_VS_ACTUAL.flatMap((p) => [p.actual, p.predicted]);
    const lo = Math.floor(Math.min(...vals)) - 1;
    const hi = Math.ceil(Math.max(...vals)) + 1;

    new Chart(paEl.getContext("2d"), {
      type: "scatter",
      data: {
        datasets: [
          {
            label: "Perfect prediction",
            type: "line",
            data: [
              { x: lo, y: lo },
              { x: hi, y: hi },
            ],
            borderColor: AMBER,
            borderDash: [6, 5],
            borderWidth: 2,
            pointRadius: 0,
          },
          {
            label: "Countries",
            data: PRED_VS_ACTUAL.map((p) => ({ x: p.actual, y: p.predicted, country: p.country })),
            backgroundColor: DEEP_BLUE + "cc",
            borderColor: "#ffffff",
            borderWidth: 1,
            radius: 5,
            hoverRadius: 7,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: { color: INK_SOFT, font: { family: "IBM Plex Sans", size: 11 } },
          },
          tooltip: {
            backgroundColor: MIDNIGHT,
            titleFont: { family: "IBM Plex Mono" },
            bodyFont: { family: "IBM Plex Mono" },
            callbacks: {
              title: (items) => (items[0].raw.country ? items[0].raw.country : ""),
              label: (item) => `Actual: ${item.parsed.x}%  |  Predicted: ${item.parsed.y.toFixed(2)}%`,
            },
          },
        },
        scales: {
          x: {
            min: lo,
            max: hi,
            title: { display: true, text: "Actual Rate (%)", color: INK_SOFT, font: { family: "IBM Plex Sans", size: 11 } },
            grid: { color: LINE },
            ticks: { color: INK_SOFT, font: { family: "IBM Plex Mono", size: 10 } },
          },
          y: {
            min: lo,
            max: hi,
            title: { display: true, text: "Predicted Rate (%)", color: INK_SOFT, font: { family: "IBM Plex Sans", size: 11 } },
            grid: { color: LINE },
            ticks: { color: INK_SOFT, font: { family: "IBM Plex Mono", size: 10 } },
          },
        },
      },
    });
  }
})();
