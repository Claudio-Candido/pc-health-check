document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector("[data-sidebar-toggle]");
  const sidebar = document.querySelector("[data-sidebar]");
  if (toggle && sidebar) {
    toggle.addEventListener("click", () => sidebar.classList.toggle("open"));
  }

  document.querySelectorAll("[data-default-today]").forEach((input) => {
    if (!input.value) {
      input.value = new Date().toISOString().slice(0, 10);
    }
  });

  document.querySelectorAll("[data-service-check]").forEach((checkbox) => {
    const target = document.querySelector(checkbox.dataset.serviceCheck);
    if (!target) return;
    const sync = () => {
      target.disabled = !checkbox.checked;
      if (!checkbox.checked) target.value = "";
    };
    checkbox.addEventListener("change", sync);
    sync();
  });
});
