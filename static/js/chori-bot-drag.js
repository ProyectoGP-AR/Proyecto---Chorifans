document.addEventListener("DOMContentLoaded", () => {
  const widget = document.getElementById("chori-bot-widget");
  const bubble = document.getElementById("chori-bot-bubble");
  const toggle = document.getElementById("chori-bot-toggle");
  const panel = document.getElementById("chori-bot-panel");
  const panelHeader = document.querySelector(".chori-bot-panel__header");

  if (!widget || !toggle) {
    return;
  }

  const STORAGE_KEY = "chori_bot_widget_position_v1";
  const SCREEN_MARGIN = 8;

  const dragState = {
    dragging: false,
    moved: false,
    suppressToggleClick: false,
    pointerId: null,
    startX: 0,
    startY: 0,
    originLeft: 0,
    originTop: 0,
  };

  function setWidgetPosition(left, top) {
    widget.style.left = `${left}px`;
    widget.style.top = `${top}px`;
    widget.style.right = "auto";
    widget.style.bottom = "auto";
  }

  function getWidgetRect() {
    return widget.getBoundingClientRect();
  }

  function clampPosition(left, top) {
    const rect = getWidgetRect();
    const width = rect.width;
    const height = rect.height;

    const maxLeft = Math.max(SCREEN_MARGIN, window.innerWidth - width - SCREEN_MARGIN);
    const maxTop = Math.max(SCREEN_MARGIN, window.innerHeight - height - SCREEN_MARGIN);

    return {
      left: Math.min(Math.max(SCREEN_MARGIN, left), maxLeft),
      top: Math.min(Math.max(SCREEN_MARGIN, top), maxTop),
    };
  }

  function savePosition() {
    try {
      const rect = getWidgetRect();
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          left: Math.round(rect.left),
          top: Math.round(rect.top),
        })
      );
    } catch (error) {
      console.warn("No se pudo guardar la posición del chatbot.", error);
    }
  }

  function loadSavedPosition() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) {
        return null;
      }
      const parsed = JSON.parse(raw);
      if (
        typeof parsed.left !== "number" ||
        typeof parsed.top !== "number"
      ) {
        return null;
      }
      return parsed;
    } catch (error) {
      return null;
    }
  }

  function clampWidgetToViewport() {
    const rect = getWidgetRect();
    const next = clampPosition(rect.left, rect.top);
    setWidgetPosition(next.left, next.top);
    savePosition();
  }

  window.clampChoriBotWidgetToViewport = clampWidgetToViewport;

  function initializeWidgetPosition() {
    const saved = loadSavedPosition();

    if (saved) {
      setWidgetPosition(saved.left, saved.top);
    } else {
      const rect = getWidgetRect();
      setWidgetPosition(rect.left, rect.top);
    }

    requestAnimationFrame(() => {
      clampWidgetToViewport();
    });
  }

  function isIgnoredTarget(target) {
    return Boolean(
      target.closest(
        "#chori-bot-bubble-close, #chori-bot-close, #chori-bot-form, #chori-bot-input, .chori-bot-send, a, input, textarea, select"
      )
    );
  }

  function beginDrag(event) {
    if (isIgnoredTarget(event.target)) {
      return;
    }

    if (event.button !== undefined && event.button !== 0) {
      return;
    }

    const rect = getWidgetRect();

    dragState.dragging = true;
    dragState.moved = false;
    dragState.pointerId = event.pointerId ?? null;
    dragState.startX = event.clientX;
    dragState.startY = event.clientY;
    dragState.originLeft = rect.left;
    dragState.originTop = rect.top;

    widget.classList.add("is-dragging");

    if (event.currentTarget && event.currentTarget.setPointerCapture && event.pointerId !== undefined) {
      try {
        event.currentTarget.setPointerCapture(event.pointerId);
      } catch (error) {
        // noop
      }
    }

    if (event.preventDefault) {
      event.preventDefault();
    }
  }

  function handleDrag(event) {
    if (!dragState.dragging) {
      return;
    }

    if (
      dragState.pointerId !== null &&
      event.pointerId !== undefined &&
      event.pointerId !== dragState.pointerId
    ) {
      return;
    }

    const deltaX = event.clientX - dragState.startX;
    const deltaY = event.clientY - dragState.startY;

    if (!dragState.moved && (Math.abs(deltaX) > 6 || Math.abs(deltaY) > 6)) {
      dragState.moved = true;
    }

    if (!dragState.moved) {
      return;
    }

    const next = clampPosition(
      dragState.originLeft + deltaX,
      dragState.originTop + deltaY
    );

    setWidgetPosition(next.left, next.top);

    if (event.preventDefault) {
      event.preventDefault();
    }
  }

  function endDrag(event) {
    if (!dragState.dragging) {
      return;
    }

    if (
      dragState.pointerId !== null &&
      event &&
      event.pointerId !== undefined &&
      event.pointerId !== dragState.pointerId
    ) {
      return;
    }

    widget.classList.remove("is-dragging");

    if (dragState.moved) {
      savePosition();
      dragState.suppressToggleClick = true;

      window.setTimeout(() => {
        dragState.suppressToggleClick = false;
      }, 180);
    }

    dragState.dragging = false;
    dragState.pointerId = null;
  }

  const dragHandles = [bubble, toggle, panelHeader].filter(Boolean);

  dragHandles.forEach((handle) => {
    handle.addEventListener("pointerdown", beginDrag);
    handle.addEventListener("dragstart", (event) => event.preventDefault());
  });

  document.addEventListener("pointermove", handleDrag, { passive: false });
  document.addEventListener("pointerup", endDrag);
  document.addEventListener("pointercancel", endDrag);

  toggle.addEventListener(
    "click",
    (event) => {
      if (dragState.suppressToggleClick) {
        event.preventDefault();
        event.stopImmediatePropagation();
      }
    },
    true
  );

  window.addEventListener("resize", () => {
    clampWidgetToViewport();
  });

  window.addEventListener("orientationchange", () => {
    window.setTimeout(() => {
      clampWidgetToViewport();
    }, 120);
  });

  initializeWidgetPosition();
});