/**
 * EduRank — Main JavaScript
 * Handles: Favorites toggle, Compare system, UI interactions
 */

"use strict";

// ═══════════════════════════════════════════════════════════════
// FAVORITES — Toggle via AJAX
// ═══════════════════════════════════════════════════════════════

/**
 * Toggle a college favorite/unfavorite via AJAX.
 * @param {number} collegeId — Database college ID
 * @param {HTMLElement} btn — The button element clicked
 */
async function toggleFavorite(collegeId, button) {

    try {

        const response = await fetch(
            `/favorites/toggle/${collegeId}`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            }
        );

        const data = await response.json();

        if (data.status === "added") {

            button.classList.add("active");

            button.innerHTML =
                '<i class="bi bi-heart-fill"></i>';

        } else if (data.status === "removed") {

            button.classList.remove("active");

            button.innerHTML =
                '<i class="bi bi-heart"></i>';
        }

    } catch (error) {

        console.error(
            "Favorite toggle failed:",
            error
        );
    }
}

// ═══════════════════════════════════════════════════════════════
// COMPARE SYSTEM
// ═══════════════════════════════════════════════════════════════

const MAX_COMPARE = 4;
let compareList = JSON.parse(sessionStorage.getItem("edurank_compare") || "[]");

/**
 * Add a college to comparison list.
 * @param {number} id — College ID
 * @param {string} name — College name
 */
function addToCompare(id, name) {
  // Check if already in list
  if (compareList.find((c) => c.id === id)) {
    showToast(`${name} is already in your comparison.`, "warning");
    return;
  }
  if (compareList.length >= MAX_COMPARE) {
    showToast(`You can compare up to ${MAX_COMPARE} colleges at once.`, "warning");
    return;
  }

  compareList.push({ id, name });
  sessionStorage.setItem("edurank_compare", JSON.stringify(compareList));
  updateCompareTray();
  showToast(`${name.split(" ").slice(0, 3).join(" ")} added to comparison.`, "success");
}

function removeFromCompare(id) {
  compareList = compareList.filter((c) => c.id !== id);
  sessionStorage.setItem("edurank_compare", JSON.stringify(compareList));
  updateCompareTray();
}

function updateCompareTray() {
  const tray = document.getElementById("compareTray");
  const list = document.getElementById("compareList");
  const btn = document.getElementById("compareBtn");
  const countBadge = document.getElementById("compareCount");
  // Also update dashboard compare count
  const dashCount = document.getElementById("compareCount");

  if (!tray || !list) return;

  tray.classList.toggle("d-none", compareList.length === 0);
  if (countBadge) countBadge.textContent = compareList.length;

  list.innerHTML = compareList
    .map(
      (c) => `
    <div class="d-flex align-items-center gap-2 py-1">
      <span class="flex-grow-1 small text-truncate fw-semibold">${c.name}</span>
      <button class="btn btn-sm btn-outline-danger py-0 px-1" onclick="removeFromCompare(${c.id})" title="Remove">
        <i class="bi bi-x"></i>
      </button>
    </div>`
    )
    .join("");

  if (btn) {
    btn.classList.toggle("d-none", compareList.length < 2);
    const ids = compareList.map((c) => c.id).join("&ids=");
    btn.href = `/compare?ids=${ids}`;
  }

  // Update fixed compare tray (favorites page)
  const fixedTray = document.getElementById("compareTrayFixed");
  const fixedLabel = document.getElementById("compareTrayLabel");
  const fixedBtn = document.getElementById("compareTrayBtn");
  if (fixedTray) {
    fixedTray.classList.toggle("d-none", compareList.length < 2);
    if (fixedLabel) fixedLabel.textContent = `${compareList.length} colleges selected`;
    if (fixedBtn) {
      const ids = compareList.map((c) => c.id).join("&ids=");
      fixedBtn.href = `/compare?ids=${ids}`;
    }
  }
}

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

  // Auto-dismiss after 3.5s
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
    container.style.cssText =
      "position: fixed; top: 80px; right: 20px; z-index: 9999; display: flex; flex-direction: column; gap: 8px;";
    document.body.appendChild(container);
    // Inject animation keyframes once
    const style = document.createElement("style");
    style.textContent = `@keyframes slideInToast { from { opacity:0; transform: translateX(20px); } to { opacity:1; transform: translateX(0); } }`;
    document.head.appendChild(style);
  }
  return container;
}

// ═══════════════════════════════════════════════════════════════
// CSRF TOKEN HELPER
// ═══════════════════════════════════════════════════════════════

function getCsrfToken() {
  // Get CSRF token from meta tag (set in base.html) or hidden input
  const meta = document.querySelector('meta[name="csrf-token"]');
  if (meta) return meta.getAttribute("content");
  const input = document.querySelector('input[name="csrf_token"]');
  if (input) return input.value;
  return "";
}

// ═══════════════════════════════════════════════════════════════
// AUTO-SUBMIT SEARCH FILTERS
// ═══════════════════════════════════════════════════════════════

function initSearchAutoSubmit() {
  const form = document.getElementById("searchForm");
  if (!form) return;

  // Auto-submit on select changes
  const selects = form.querySelectorAll("select");
  selects.forEach((sel) => {
    sel.addEventListener("change", () => form.submit());
  });

  // Auto-submit on checkbox change
  const checkboxes = form.querySelectorAll('input[type="checkbox"]');
  checkboxes.forEach((cb) => {
    cb.addEventListener("change", () => form.submit());
  });
}

// ═══════════════════════════════════════════════════════════════
// STICKY COMPARE BAR (College Detail)
// ═══════════════════════════════════════════════════════════════

function initStickyCompare() {
  // Show a sticky bar at the bottom if user has items to compare
  if (compareList.length >= 2) {
    const bar = document.createElement("div");
    bar.style.cssText = `
      position: fixed; bottom: 0; left: 0; right: 0; z-index: 100;
      background: #4f46e5; color: #fff;
      padding: 12px 24px; display: flex; align-items: center; justify-content: center; gap: 16px;
      font-family: 'DM Sans', sans-serif; font-size: 14px; font-weight: 600;
    `;
    const ids = compareList.map((c) => c.id).join("&ids=");
    bar.innerHTML = `
      <span>${compareList.length} colleges in comparison</span>
      <a href="/compare?ids=${ids}" style="background:#fff;color:#4f46e5;padding:6px 16px;border-radius:8px;text-decoration:none;font-weight:700;">
        Compare Now →
      </a>
      <button onclick="this.parentElement.remove()" style="background:none;border:none;color:rgba(255,255,255,.6);cursor:pointer;font-size:20px;">×</button>
    `;
    document.body.appendChild(bar);
    // Offset footer
    document.body.style.paddingBottom = "56px";
  }
}

// ═══════════════════════════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════════════════════════

document.addEventListener("DOMContentLoaded", () => {
  updateCompareTray();
  initSearchAutoSubmit();
  initStickyCompare();

  // Auto-dismiss alerts after 5s
  document.querySelectorAll(".edu-alert").forEach((alert) => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert?.close();
    }, 5000);
  });
});
let compareList = [];


function addToCompare(collegeId, collegeName) {

    if (compareList.includes(collegeId)) {
        alert(collegeName + " is already added.");
        return;
    }

    if (compareList.length >= 3) {
        alert("You can compare maximum 3 colleges.");
        return;
    }

    compareList.push(collegeId);

    alert(collegeName + " added to compare.");

    if (compareList.length >= 2) {

        const query = compareList
            .map(id => "ids=" + id)
            .join("&");

        window.location.href =
            "/colleges/compare?" + query;
    }
}
document.addEventListener("DOMContentLoaded", () => {
  updateCompareTray();
});