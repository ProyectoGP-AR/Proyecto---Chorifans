document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("mobile-menu-toggle");
  const panel = document.getElementById("mobile-menu-panel");

  if (!toggle || !panel) {
    return;
  }

  const closeMenu = () => {
    panel.classList.remove("is-open");
    panel.setAttribute("aria-hidden", "true");
    toggle.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", "false");
    document.body.classList.remove("mobile-menu-open");
  };

  const openMenu = () => {
    panel.classList.add("is-open");
    panel.setAttribute("aria-hidden", "false");
    toggle.classList.add("is-open");
    toggle.setAttribute("aria-expanded", "true");
    document.body.classList.add("mobile-menu-open");
  };

  toggle.addEventListener("click", () => {
    if (panel.classList.contains("is-open")) {
      closeMenu();
    } else {
      openMenu();
    }
  });

  panel.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", closeMenu);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeMenu();
    }
  });

  document.addEventListener("click", (event) => {
    if (
      panel.classList.contains("is-open") &&
      !panel.contains(event.target) &&
      !toggle.contains(event.target)
    ) {
      closeMenu();
    }
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth > 768) {
      closeMenu();
    }
  });
});