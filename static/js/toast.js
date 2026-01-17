(function () {
  const containerId = "toaster";

  function createToast({
    title,
    description,
    variant = "info",
    duration = 4000,
    action,
    cancel
  }) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast toast-${variant}`;

    toast.innerHTML = `
      <div class="toast-title">${title}</div>
      ${description ? `<div class="toast-description">${description}</div>` : ""}
      ${
        action || cancel
          ? `<div class="toast-actions">
              ${
                action
                  ? `<button class="toast-btn toast-btn-primary">${action.label}</button>`
                  : ""
              }
              ${
                cancel
                  ? `<button class="toast-btn toast-btn-muted">${cancel.label}</button>`
                  : ""
              }
            </div>`
          : ""
      }
    `;

    container.appendChild(toast);

    function dismiss() {
      toast.classList.add("animate-toast-out");
      setTimeout(() => toast.remove(), 150);
    }

    if (action?.onClick) {
      toast
        .querySelector(".toast-btn-primary")
        ?.addEventListener("click", () => {
          action.onClick();
          dismiss();
        });
    }

    if (cancel?.onClick) {
      toast
        .querySelector(".toast-btn-muted")
        ?.addEventListener("click", () => {
          cancel.onClick();
          dismiss();
        });
    }

    if (duration !== Infinity) {
      setTimeout(dismiss, duration);
    }
  }

  // ==========================
  // API pública (window.toast)
  // ==========================
  window.toast = {
    success: (title, opts = {}) =>
      createToast({ title, variant: "success", ...opts }),

    error: (title, opts = {}) =>
      createToast({ title, variant: "error", ...opts }),

    info: (title, opts = {}) =>
      createToast({ title, variant: "info", ...opts }),

    warning: (title, opts = {}) =>
      createToast({ title, variant: "warning", ...opts }),
  };

  // ==========================
  // Integração GLOBAL com htmx
  // ==========================
  document.body.addEventListener("htmx:responseError", () => {
    window.toast.error("Erro inesperado", {
      description: "Não foi possível processar sua solicitação.",
    });
  });

})();
