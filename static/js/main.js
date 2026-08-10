(function () {
  const toggle = document.getElementById("navToggle");
  const rail = document.getElementById("rail");
  if (!toggle || !rail) return;

  toggle.addEventListener("click", () => {
    const isOpen = rail.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", String(isOpen));
  });

  document.addEventListener("click", (e) => {
    if (!rail.contains(e.target) && !toggle.contains(e.target)) {
      rail.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
    }
  });
})();
