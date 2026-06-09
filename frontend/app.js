const API_BASE = window.location.port === "8000" ? "" : "http://127.0.0.1:8000";
const REFRESH_INTERVAL_MS = 60_000;

const tableBody = document.getElementById("statusTableBody");
const form = document.getElementById("urlForm");
const nameInput = document.getElementById("nameInput");
const urlInput = document.getElementById("urlInput");
const formMessage = document.getElementById("formMessage");
const refreshButton = document.getElementById("refreshButton");
const lastUpdated = document.getElementById("lastUpdated");
const addPanel = document.getElementById("addUrlPanel");
const toggleAddPanelButton = document.getElementById("toggleAddPanel");

function setAddPanelVisibility(show) {
    addPanel.classList.toggle("is-collapsed", !show);
    toggleAddPanelButton.setAttribute("aria-expanded", show ? "true" : "false");
    toggleAddPanelButton.textContent = show ? "-" : "+";
}

function lastUpdatedLabel() {
    return `Last updated: ${new Date().toLocaleTimeString("en-IN", { timeZone: "Asia/Kolkata" })} IST`;
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function renderRows(items) {
    if (!items.length) {
        tableBody.innerHTML = '<tr><td colspan="7" class="empty-state">No URLs registered yet.</td></tr>';
        return;
    }

    tableBody.innerHTML = items.map((item) => {
        const latest = item.latest;
        const status = latest?.status ?? "pending";
        const statusClass = status === "up" ? "status-up" : "status-down";
        const statusLabel = latest ? status.toUpperCase() : "PENDING";
        const code = latest?.status_code ?? "-";
        const responseTime = latest?.response_time_ms != null ? `${latest.response_time_ms} ms` : "-";
        const warningSymbol = latest?.slow_alert ? '<span class="warn-symbol" title="Slow response">⚠</span>' : "";
        const checkedAt = latest?.checked_at ?? "Waiting for first check";
        const error = latest?.error ?? "-";

        return `
            <tr>
                <td>${escapeHtml(item.name || "-")}</td>
                <td class="url-text">${escapeHtml(item.url)}</td>
                <td><span class="status-pill ${statusClass}">${escapeHtml(statusLabel)}</span></td>
                <td>${escapeHtml(code)}</td>
                <td>${escapeHtml(responseTime)} ${warningSymbol}</td>
                <td>${escapeHtml(checkedAt)}</td>
                <td class="error-text">${escapeHtml(error)}</td>
            </tr>
        `;
    }).join("");
}

async function loadUrls(options = {}) {
    const forceRefresh = options.forceRefresh === true;
    lastUpdated.textContent = "Refreshing...";
    const querySuffix = forceRefresh ? "?refresh=true" : "";
    const response = await fetch(`${API_BASE}/api/v1/urls${querySuffix}`);
    if (!response.ok) {
        throw new Error(`GET /api/v1/urls failed with ${response.status}`);
    }

    const items = await response.json();
    renderRows(items);
    lastUpdated.textContent = `${lastUpdatedLabel()}${forceRefresh ? " (manual cycle)" : ""}`;
}

async function submitUrl(event) {
    event.preventDefault();
    formMessage.textContent = "Submitting...";

    const payload = {
        name: nameInput.value.trim() || null,
        url: urlInput.value.trim(),
    };

    try {
        const response = await fetch(`${API_BASE}/api/v1/urls`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });

        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.detail || `POST /api/v1/urls failed with ${response.status}`);
        }

        form.reset();
        formMessage.textContent = "URL added successfully. Trigger Manual Check Cycle or wait for the next whole-minute auto cycle.";
        setAddPanelVisibility(false);
        await loadUrls();
    } catch (error) {
        formMessage.textContent = error.message;
    }
}

form.addEventListener("submit", submitUrl);
toggleAddPanelButton.addEventListener("click", () => {
    const isExpanded = toggleAddPanelButton.getAttribute("aria-expanded") === "true";
    setAddPanelVisibility(!isExpanded);
});

refreshButton.addEventListener("click", () => {
    loadUrls({ forceRefresh: true }).catch((error) => {
        formMessage.textContent = error.message;
        lastUpdated.textContent = "Refresh failed";
    });
});

loadUrls().catch((error) => {
    formMessage.textContent = error.message;
    lastUpdated.textContent = "Initial load failed";
});

setAddPanelVisibility(false);

setInterval(() => {
    loadUrls().catch((error) => {
        formMessage.textContent = error.message;
        lastUpdated.textContent = "Auto-refresh failed";
    });
}, REFRESH_INTERVAL_MS);
