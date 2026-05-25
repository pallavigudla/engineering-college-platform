"use strict";

// ═══════════════════════════════════════════════════════════════
// TOAST NOTIFICATIONS
// ═══════════════════════════════════════════════════════════════

function showToast(message, type = "info") {

  const container = getOrCreateToastContainer();

  const colorMap = {
    success: "#10b981",
    danger: "#ef4444",
    warning: "#f59e0b",
    info: "#4f46e5",
  };

  const toast = document.createElement("div");

  toast.className = "edu-toast";

  toast.style.cssText = `
    background: #fff;
    border: 1px solid #e2e8f0;
    border-left: 4px solid ${colorMap[type] || colorMap.info};
    border-radius: 10px;
    padding: 12px 16px;
    box-shadow: 0 4px 16px rgba(0,0,0,.12);
    font-size: 14px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    color: #1e293b;
    max-width: 320px;
    animation: slideInToast .3s ease forwards;
    cursor: pointer;
  `;

  toast.textContent = message;

  toast.onclick = () => dismissToast(toast);

  container.appendChild(toast);

  setTimeout(() => dismissToast(toast), 3500);
}

function dismissToast(toast) {

  toast.style.opacity = "0";

  toast.style.transform = "translateX(20px)";

  toast.style.transition = "all .25s ease";

  setTimeout(() => toast.remove(), 260);
}

function getOrCreateToastContainer() {

  let container = document.getElementById("toastContainer");

  if (!container) {

    container = document.createElement("div");

    container.id = "toastContainer";

    container.style.cssText = `
      position: fixed;
      top: 80px;
      right: 20px;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 8px;
    `;

    document.body.appendChild(container);

    const style = document.createElement("style");

    style.textContent = `
      @keyframes slideInToast {
        from {
          opacity: 0;
          transform: translateX(20px);
        }

        to {
          opacity: 1;
          transform: translateX(0);
        }
      }
    `;

    document.head.appendChild(style);
  }

  return container;
}

// ═══════════════════════════════════════════════════════════════
// CSRF TOKEN HELPER
// ═══════════════════════════════════════════════════════════════

function getCsrfToken() {

  const meta = document.querySelector(
    'meta[name="csrf-token"]'
  );

  if (meta) {
    return meta.getAttribute("content");
  }

  const input = document.querySelector(
    'input[name="csrf_token"]'
  );

  if (input) {
    return input.value;
  }

  return "";
}

// ═══════════════════════════════════════════════════════════════
// AUTO SUBMIT SEARCH FILTERS
// ═══════════════════════════════════════════════════════════════

function initSearchAutoSubmit() {

  const form = document.getElementById("searchForm");

  if (!form) return;

  // Auto-submit selects
  const selects = form.querySelectorAll("select");

  selects.forEach((select) => {

    select.addEventListener("change", () => {

      form.submit();

    });

  });

  // Auto-submit checkboxes
  const checkboxes = form.querySelectorAll(
    'input[type="checkbox"]'
  );

  checkboxes.forEach((checkbox) => {

    checkbox.addEventListener("change", () => {

      form.submit();

    });

  });
}

// ═══════════════════════════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════════════════════════

document.addEventListener("DOMContentLoaded", () => {

  // Initialize auto-submit filters
  initSearchAutoSubmit();

  // Auto-dismiss alerts
  document.querySelectorAll(".edu-alert").forEach((alert) => {

    setTimeout(() => {

      const bsAlert =
        bootstrap.Alert.getOrCreateInstance(alert);

      bsAlert?.close();

    }, 5000);

  });

});