(function () {
  const DEEP_BLUE = "#06598a";
  const TEAL = "#16839a";
  const AMBER = "#e39a3c";
  const INK_SOFT = "#4a5568";
  const LINE = "#e3e7ec";

  const baseOptions = (xLabel, yLabel) => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "#17233f",
        titleFont: { family: "IBM Plex Mono" },
        bodyFont: { family: "IBM Plex Mono" },
        padding: 10,
        callbacks: {
          title: (items) => items[0].raw.country,
          label: (item) => `${xLabel}: ${item.parsed.x}  |  ${yLabel}: ${item.parsed.y}%`,
        },
      },
    },
    scales: {
      x: {
        title: { display: true, text: xLabel, color: INK_SOFT, font: { family: "IBM Plex Sans", size: 11 } },
        grid: { color: LINE },
        ticks: { color: INK_SOFT, font: { family: "IBM Plex Mono", size: 10 } },
      },
      y: {
        title: { display: true, text: yLabel, color: INK_SOFT, font: { family: "IBM Plex Sans", size: 11 } },
        grid: { color: LINE },
        ticks: { color: INK_SOFT, font: { family: "IBM Plex Mono", size: 10 } },
      },
    },
  });

  function scatter(canvasId, xKey, xLabel, yLabel, color) {
    const el = document.getElementById(canvasId);
    if (!el) return;
    const points = COUNTRIES.map((c) => ({ x: c[xKey], y: c.unemployment, country: c.country }));
    new Chart(el.getContext("2d"), {
      type: "scatter",
      data: {
        datasets: [
          {
            data: points,
            backgroundColor: color + "cc",
            borderColor: "#ffffff",
            borderWidth: 1,
            radius: 5,
            hoverRadius: 7,
          },
        ],
      },
      options: baseOptions(xLabel, yLabel),
    });
  }

  scatter("scatterGdp", "gdp", "GDP per Capita ($)", "Youth Unemployment", DEEP_BLUE);
  scatter("scatterEdu", "education", "Education Index", "Youth Unemployment", TEAL);

  // ---- sortable table ----
  const table = document.getElementById("countryTable");
  if (table) {
    const tbody = table.querySelector("tbody");
    const headers = table.querySelectorAll("th");
    let sortState = {};

    headers.forEach((th) => {
      th.addEventListener("click", () => {
        const key = th.dataset.key;
        const type = th.dataset.type;
        const idx = Array.from(th.parentElement.children).indexOf(th);
        const asc = !(sortState[key] === "asc");
        sortState = { [key]: asc ? "asc" : "desc" };

        const rows = Array.from(tbody.querySelectorAll("tr"));
        rows.sort((a, b) => {
          let av = a.children[idx].textContent.trim();
          let bv = b.children[idx].textContent.trim();
          if (type === "number") {
            av = parseFloat(av);
            bv = parseFloat(bv);
          }
          if (av < bv) return asc ? -1 : 1;
          if (av > bv) return asc ? 1 : -1;
          return 0;
        });
        rows.forEach((r) => tbody.appendChild(r));
      });
    });
  }
})();
