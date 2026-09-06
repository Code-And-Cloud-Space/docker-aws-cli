const API_BASE = "http://localhost:8000";

let currentTab = "salesforce";
let tokenCountdownInterval = null;
let isSalesforceConnected = false;
let currentSalesforceInstanceUrl = "";

function getSalesforceRecordUrl(recordId) {
  if (!recordId) return "#";
  const base = currentSalesforceInstanceUrl ? currentSalesforceInstanceUrl.replace(/\/+$/, "") : "https://login.salesforce.com";
  return `${base}/${recordId}`;
}

function renderSalesforceIdLink(recordId) {
  if (!recordId || recordId === "N/A" || recordId === "-") {
    return `<span class="font-mono text-xs text-slate-500">-</span>`;
  }
  const url = getSalesforceRecordUrl(recordId);
  return `
    <a href="${url}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1.5 font-mono text-xs text-sky-400 hover:text-sky-300 hover:underline transition group" title="Open record in Salesforce (${recordId})">
      <span>${recordId}</span>
      <i class="fa-solid fa-arrow-up-right-from-square text-[10px] text-sky-400/70 group-hover:text-sky-300 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform"></i>
    </a>
  `;
}

// -----------------------------------------------------------------------------
// Modern Toast Notification Engine
// -----------------------------------------------------------------------------
function showToast(message, type = "info", duration = 4000) {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toastId = "toast_" + Math.random().toString(36).substring(2, 9);
  
  const typeConfig = {
    success: {
      border: "border-emerald-500/40",
      bg: "bg-slate-900/95",
      accentBg: "bg-emerald-500/10",
      iconColor: "text-emerald-400",
      icon: "fa-solid fa-circle-check",
      titleColor: "text-emerald-400",
      title: "Success"
    },
    error: {
      border: "border-red-500/40",
      bg: "bg-slate-900/95",
      accentBg: "bg-red-500/10",
      iconColor: "text-red-400",
      icon: "fa-solid fa-circle-xmark",
      titleColor: "text-red-400",
      title: "Error"
    },
    warning: {
      border: "border-amber-500/40",
      bg: "bg-slate-900/95",
      accentBg: "bg-amber-500/10",
      iconColor: "text-amber-400",
      icon: "fa-solid fa-triangle-exclamation",
      titleColor: "text-amber-400",
      title: "Warning"
    },
    info: {
      border: "border-sky-500/40",
      bg: "bg-slate-900/95",
      accentBg: "bg-sky-500/10",
      iconColor: "text-sky-400",
      icon: "fa-solid fa-circle-info",
      titleColor: "text-sky-400",
      title: "Notification"
    }
  };

  const config = typeConfig[type] || typeConfig.info;

  const toast = document.createElement("div");
  toast.id = toastId;
  toast.className = `toast-item pointer-events-auto flex items-start gap-3 p-3.5 rounded-xl border ${config.border} ${config.bg} backdrop-blur-md shadow-2xl transform translate-x-full opacity-0`;
  
  toast.innerHTML = `
    <div class="p-2 rounded-lg ${config.accentBg} ${config.iconColor} shrink-0 mt-0.5">
      <i class="${config.icon} text-sm"></i>
    </div>
    <div class="flex-1 min-w-0 pr-1">
      <div class="text-[11px] font-semibold ${config.titleColor} uppercase tracking-wider mb-0.5">${config.title}</div>
      <div class="text-xs text-slate-200 leading-relaxed break-words">${message}</div>
    </div>
    <button onclick="dismissToast('${toastId}')" class="text-slate-400 hover:text-white p-1 -mr-1 -mt-1 rounded transition shrink-0">
      <i class="fa-solid fa-xmark text-xs"></i>
    </button>
  `;

  container.appendChild(toast);

  // Trigger slide-in animation
  requestAnimationFrame(() => {
    toast.classList.remove("translate-x-full", "opacity-0");
    toast.classList.add("translate-x-0", "opacity-100");
  });

  // Auto dismiss timer
  if (duration > 0) {
    setTimeout(() => {
      dismissToast(toastId);
    }, duration);
  }
}

function dismissToast(toastId) {
  const toast = document.getElementById(toastId);
  if (!toast) return;
  toast.classList.remove("translate-x-0", "opacity-100");
  toast.classList.add("translate-x-full", "opacity-0");
  setTimeout(() => {
    if (toast && toast.parentNode) {
      toast.parentNode.removeChild(toast);
    }
  }, 300);
}

// Fallback to intercept any unexpected window.alert
window.alert = function(msg) {
  showToast(String(msg), "info");
};

// -----------------------------------------------------------------------------
// Session ID Management (Per Browser Window / Incognito Isolation)
// -----------------------------------------------------------------------------
function getSessionId() {
  return sessionStorage.getItem("sf_integration_session_id") || "";
}

function setSessionId(id) {
  if (id) {
    sessionStorage.setItem("sf_integration_session_id", id);
  } else {
    sessionStorage.removeItem("sf_integration_session_id");
  }
}

function ensureSessionId() {
  let id = getSessionId();
  if (!id) {
    id = "sess_" + Math.random().toString(36).substring(2, 12) + "_" + Date.now();
    setSessionId(id);
  }
  return id;
}

function getAuthHeaders() {
  const sessId = getSessionId();
  const headers = { "Content-Type": "application/json" };
  if (sessId) {
    headers["X-Session-ID"] = sessId;
  }
  return headers;
}

function renderLockedStateForAllTabs() {
  const lockedRow = (title, msg) => `
    <tr>
      <td colspan="10" class="py-12 text-center text-amber-400 font-medium">
        <div class="flex flex-col items-center justify-center space-y-2">
          <i class="fa-solid fa-lock text-3xl text-amber-500"></i>
          <span class="text-sm font-semibold">${title}</span>
          <span class="text-xs text-slate-400">${msg || 'Please connect your Live Salesforce account using the "Connect Live Salesforce" button above.'}</span>
        </div>
      </td>
    </tr>
  `;

  const sfTbody = document.getElementById("sf-table-body");
  if (sfTbody) sfTbody.innerHTML = lockedRow("Salesforce Connection Required", "Please connect to Salesforce using the button above to view live records.");

  const mysqlTbody = document.getElementById("mysql-table-body");
  if (mysqlTbody) mysqlTbody.innerHTML = lockedRow("Salesforce Connection Required", "Please connect to Salesforce to view synchronized MySQL database records.");

  const ddbTbody = document.getElementById("dynamodb-table-body");
  if (ddbTbody) ddbTbody.innerHTML = lockedRow("Salesforce Connection Required", "Please connect to Salesforce to view AWS DynamoDB items.");

  const s3Tbody = document.getElementById("s3-table-body");
  if (s3Tbody) s3Tbody.innerHTML = lockedRow("Salesforce Connection Required", "Please connect to Salesforce to view AWS S3 event archives.");

  const secretsTbody = document.getElementById("secrets-table-body");
  if (secretsTbody) secretsTbody.innerHTML = lockedRow("Salesforce Connection Required", "Please connect to Salesforce to view AWS Secrets Manager tokens.");

  const sqsCards = document.getElementById("sqs-cards");
  if (sqsCards) {
    sqsCards.innerHTML = `
      <div class="col-span-2 text-center text-amber-400 py-12 border border-amber-900/40 bg-amber-950/20 rounded-xl space-y-2">
        <i class="fa-solid fa-lock text-3xl text-amber-500"></i>
        <p class="text-sm font-semibold">Salesforce Connection Required</p>
        <p class="text-xs text-slate-400">Please connect to Salesforce using the button above to view AWS SQS message queues.</p>
      </div>
    `;
  }

  const logsContainer = document.getElementById("logs-container");
  if (logsContainer) {
    logsContainer.innerHTML = `
      <div class="text-amber-400 text-center py-12 border border-amber-900/40 bg-amber-950/20 rounded-xl space-y-2">
        <i class="fa-solid fa-lock text-3xl text-amber-500"></i>
        <p class="text-sm font-semibold">Salesforce Connection Required</p>
        <p class="text-xs text-slate-400">Please connect to Salesforce using the button above to view integration audit logs.</p>
      </div>
    `;
  }

  const studioTbody = document.getElementById("custom-query-tbody");
  if (studioTbody) studioTbody.innerHTML = lockedRow("Salesforce Connection Required", "Please connect to Salesforce to use the Admin Custom Mapping Studio.");

  const logCount = document.getElementById("log-count");
  if (logCount) logCount.textContent = "0";
}

function switchTab(tabId) {
  if (tabId === "sync" && !isSalesforceConnected) {
    tabId = "salesforce";
  }
  currentTab = tabId;
  ["salesforce", "mysql", "dynamodb", "s3", "sqs", "secrets", "admin-mapping", "sync", "logs"].forEach(t => {
    const el = document.getElementById(`tab-${t}`);
    const btn = document.getElementById(`tab-btn-${t}`);
    if (el) el.classList.toggle("hidden", t !== tabId);
    if (btn) btn.classList.toggle("tab-active", t === tabId);
  });

  if (!isSalesforceConnected) {
    renderLockedStateForAllTabs();
    return;
  }

  if (tabId === "salesforce") loadSalesforceRecords();
  if (tabId === "mysql") loadMySQLRecords();
  if (tabId === "dynamodb") loadDynamoDBRecords();
  if (tabId === "s3") loadS3Files();
  if (tabId === "sqs") loadSQSStats();
  if (tabId === "secrets") loadSecrets();
  if (tabId === "admin-mapping") initAdminMappingStudio();
  if (tabId === "logs") loadLogs();
}

function handleOAuthParams() {
  const params = new URLSearchParams(window.location.search);
  const alertEl = document.getElementById("oauth-alert");
  const alertText = document.getElementById("oauth-alert-text");

  const urlSessionId = params.get("session_id");
  if (urlSessionId) {
    setSessionId(urlSessionId);
  }

  if (params.get("auth_success") === "true") {
    alertEl.className = "px-4 py-2.5 text-xs text-center font-medium transition flex items-center justify-between bg-emerald-950/90 text-emerald-300 border-b border-emerald-800";
    alertText.innerHTML = `<i class="fa-solid fa-circle-check mr-2"></i> Successfully connected to Live Salesforce via OAuth 2.0 Auth Code Flow (PKCE S256)! Tokens secured in Secrets Manager & MySQL.`;
    alertEl.classList.remove("hidden");
    showToast("Successfully connected to Live Salesforce via OAuth 2.0 Auth Code Flow (PKCE S256)!", "success", 6000);
    window.history.replaceState({}, document.title, window.location.pathname);
  } else if (params.get("auth_error")) {
    alertEl.className = "px-4 py-2.5 text-xs text-center font-medium transition flex items-center justify-between bg-red-950/90 text-red-300 border-b border-red-800";
    alertText.innerHTML = `<i class="fa-solid fa-triangle-exclamation mr-2"></i> ${params.get("auth_error")}`;
    alertEl.classList.remove("hidden");
    showToast(`OAuth Error: ${params.get("auth_error")}`, "error", 6000);
    window.history.replaceState({}, document.title, window.location.pathname);
  }
}

function dismissAlert() {
  document.getElementById("oauth-alert").classList.add("hidden");
}

async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/api/status`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    
    // AWS Health Badge
    const awsEl = document.getElementById("aws-health");
    if (data.aws && data.aws.status === "connected") {
      awsEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-400"></span><span class="text-emerald-300">AWS: LocalStack Online</span>`;
    } else {
      awsEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-red-400"></span><span class="text-red-300">AWS: Offline</span>`;
    }

    // Salesforce Session Details & Countdown
    updateSessionBar(data.salesforce);

    // Update log count
    const logEl = document.getElementById("log-count");
    if (logEl) {
      logEl.textContent = isSalesforceConnected ? (data.recentLogsCount || 0) : 0;
    }
  } catch (err) {
    console.error("Health check error:", err);
    updateSessionBar({ status: "disconnected" });
  }
}

function updateSessionBar(sf) {
  const statusBadge = document.getElementById("session-status-badge");
  const detailsGroup = document.getElementById("session-details-group");
  const btnLogin = document.getElementById("btn-oauth-login");
  const btnRefresh = document.getElementById("btn-oauth-refresh");
  const btnDisconnect = document.getElementById("btn-oauth-disconnect");
  const sfHealthEl = document.getElementById("sf-health");
  const syncBtn = document.getElementById("tab-btn-sync");

  if (!sf || sf.status === "disconnected") {
    isSalesforceConnected = false;
    currentSalesforceInstanceUrl = "";
    statusBadge.className = "px-2 py-0.5 rounded text-[11px] bg-slate-800 text-slate-400 border border-slate-700";
    statusBadge.textContent = "Not Connected";
    detailsGroup.classList.add("hidden");
    btnLogin.classList.remove("hidden");
    btnRefresh.classList.add("hidden");
    btnDisconnect.classList.add("hidden");
    sfHealthEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-slate-500"></span><span class="text-slate-400">SF: Not Connected</span>`;
    clearInterval(tokenCountdownInterval);

    // Hide the Sync Pipeline tab button when not logged in
    if (syncBtn) syncBtn.classList.add("hidden");
    if (currentTab === "sync") switchTab("salesforce");

    // Completely clear and lock all data displays across the dashboard
    renderLockedStateForAllTabs();
  } else {
    isSalesforceConnected = true;
    currentSalesforceInstanceUrl = sf.instanceUrl || "";
    const isExpired = sf.isExpired;
    statusBadge.className = isExpired ? "px-2 py-0.5 rounded text-[11px] bg-amber-900/50 text-amber-300 border border-amber-800" : "px-2 py-0.5 rounded text-[11px] bg-emerald-900/50 text-emerald-300 border border-emerald-700";
    statusBadge.textContent = isExpired ? "Token Expired (Auto-Refreshes)" : "Connected (Live)";

    detailsGroup.classList.remove("hidden");
    document.getElementById("session-org-id").textContent = sf.salesforceOrgId || "N/A";
    
    const instanceEl = document.getElementById("session-instance-url");
    if (instanceEl) {
      if (sf.instanceUrl) {
        instanceEl.innerHTML = `<a href="${sf.instanceUrl}" target="_blank" rel="noopener noreferrer" class="text-cyan-400 hover:text-cyan-300 hover:underline inline-flex items-center gap-1 font-mono">${sf.instanceUrl} <i class="fa-solid fa-arrow-up-right-from-square text-[9px]"></i></a>`;
      } else {
        instanceEl.textContent = "N/A";
      }
    }

    btnLogin.classList.add("hidden");
    btnRefresh.classList.remove("hidden");
    btnDisconnect.classList.remove("hidden");

    // Show the Sync Pipeline tab button when logged in
    if (syncBtn) syncBtn.classList.remove("hidden");

    sfHealthEl.innerHTML = `<span class="w-2 h-2 rounded-full ${isExpired ? 'bg-amber-400' : 'bg-emerald-400'}"></span><span class="${isExpired ? 'text-amber-300' : 'text-emerald-300'}">SF: ${isExpired ? 'Expiring' : 'Active'}</span>`;

    // Start live countdown
    startCountdown(sf.expiresInSeconds || 0);
  }
}

function startCountdown(totalSeconds) {
  clearInterval(tokenCountdownInterval);
  let remaining = totalSeconds;

  function renderTime() {
    const el = document.getElementById("session-countdown");
    if (!el) return;
    if (remaining <= 0) {
      el.textContent = "Expired (Refreshes on next API call)";
      el.className = "text-amber-400 font-bold";
      return;
    }
    const hours = Math.floor(remaining / 3600);
    const mins = Math.floor((remaining % 3600) / 60);
    const secs = remaining % 60;
    el.textContent = `${hours}h ${mins}m ${secs}s`;
    el.className = remaining < 300 ? "text-red-400 font-bold animate-pulse" : "text-amber-300 font-semibold";
  }

  renderTime();
  tokenCountdownInterval = setInterval(() => {
    remaining = Math.max(0, remaining - 1);
    renderTime();
  }, 1000);
}

// -----------------------------------------------------------------------------
// OAuth Actions
// -----------------------------------------------------------------------------
async function startSalesforceLogin() {
  try {
    const sessId = ensureSessionId();
    const res = await fetch(`${API_BASE}/api/auth/salesforce/login?session_id=${encodeURIComponent(sessId)}`);
    const data = await res.json();
    if (data.authUrl) {
      window.location.href = data.authUrl;
    } else {
      showToast("Failed to generate Salesforce OAuth URL. Please check .env credentials.", "error");
    }
  } catch (err) {
    showToast(`OAuth Login error: ${err.message}`, "error");
  }
}

async function forceRefreshToken() {
  const sessId = getSessionId();
  if (!sessId) {
    showToast("Please connect to Salesforce first.", "warning");
    return;
  }
  try {
    const res = await fetch(`${API_BASE}/api/auth/salesforce/refresh`, {
      method: "POST",
      headers: getAuthHeaders()
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Refresh failed");
    showToast(`Token Refreshed via AWS Secrets Manager! Instance: ${data.instanceUrl}`, "success");
    refreshAll();
  } catch (err) {
    showToast(`Refresh Failed: ${err.message}`, "error");
  }
}

async function disconnectSalesforce() {
  const sessId = getSessionId();
  if (!sessId) {
    showToast("No active session to disconnect.", "warning");
    return;
  }
  if (!confirm("Disconnect active Salesforce account for this session?")) return;
  try {
    await fetch(`${API_BASE}/api/auth/salesforce/disconnect`, {
      method: "POST",
      headers: getAuthHeaders()
    });
    setSessionId(null);
    isSalesforceConnected = false;
    showToast("Salesforce session disconnected successfully.", "info");
    refreshAll();
  } catch (err) {
    showToast(`Disconnect error: ${err.message}`, "error");
  }
}

// -----------------------------------------------------------------------------
// Data Explorers
// -----------------------------------------------------------------------------
async function loadSalesforceRecords() {
  const sobject = document.getElementById("sf-object-select").value;
  const tbody = document.getElementById("sf-table-body");

  if (!isSalesforceConnected || !getSessionId()) {
    tbody.innerHTML = `<tr><td colspan="5" class="py-12 text-center text-amber-400 font-medium"><div class="flex flex-col items-center justify-center space-y-2"><i class="fa-solid fa-lock text-3xl text-amber-500"></i><span class="text-sm font-semibold">Salesforce Connection Required</span><span class="text-xs text-slate-400">Please connect to Salesforce using the "Connect Live Salesforce" button above to view live records.</span></div></td></tr>`;
    return;
  }

  tbody.innerHTML = `<tr><td colspan="5" class="py-8 text-center text-slate-500"><i class="fa-solid fa-spinner animate-spin mr-2"></i>Loading ${sobject}s from Live Salesforce...</td></tr>`;

  try {
    const res = await fetch(`${API_BASE}/api/salesforce/records/${sobject}`, {
      headers: getAuthHeaders()
    });
    
    if (res.status === 401) {
      isSalesforceConnected = false;
      renderLockedStateForAllTabs();
      return;
    }

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      tbody.innerHTML = `<tr><td colspan="5" class="py-8 text-center text-amber-400 font-medium"><i class="fa-solid fa-lock mr-2"></i>Please connect to Salesforce using the "Connect Live Salesforce" button above. (${errData.detail || "Authentication required"})</td></tr>`;
      return;
    }

    const data = await res.json();
    const records = data.records || [];

    if (records.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" class="py-8 text-center text-slate-500">No ${sobject} records found in Live Salesforce.</td></tr>`;
      return;
    }

    tbody.innerHTML = records.map(r => {
      const name = r.Name || `${r.FirstName || ''} ${r.LastName || ''}` || r.Title || "N/A";
      const extra = r.Industry || r.Email || (r.Amount ? `$${Number(r.Amount).toLocaleString()}` : r.Company || "-");
      const modDate = r.LastModifiedDate ? new Date(r.LastModifiedDate).toLocaleString() : "N/A";

      return `
        <tr class="hover:bg-slate-800/50 transition">
          <td class="py-3 px-4">${renderSalesforceIdLink(r.Id)}</td>
          <td class="py-3 px-4 font-medium text-white">${name}</td>
          <td class="py-3 px-4 text-xs text-slate-400">${extra}</td>
          <td class="py-3 px-4 text-xs text-slate-500">${modDate}</td>
          <td class="py-3 px-4 text-right">
            <button onclick="syncSingleRecord('${sobject}', '${r.Id}')" class="text-xs bg-slate-800 hover:bg-slate-700 text-cyan-400 hover:text-cyan-300 px-2.5 py-1.5 rounded border border-slate-700 transition">
              <i class="fa-solid fa-cloud-arrow-up mr-1"></i> Sync to AWS & DB
            </button>
          </td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="5" class="py-8 text-center text-amber-400 font-medium"><i class="fa-solid fa-lock mr-2"></i>Please connect to Salesforce using the "Connect Live Salesforce" button above. (${err.message})</td></tr>`;
  }
}

async function syncSingleRecord(sobject, recordId) {
  const sessId = getSessionId();
  if (!isSalesforceConnected || !sessId) {
    showToast("Please connect to Salesforce first using the Connect Live Salesforce button.", "warning");
    return;
  }
  try {
    const res = await fetch(`${API_BASE}/api/sync/record`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ sobject, record_id: recordId, session_id: sessId })
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Failed to sync record");
    }
    showToast(`Successfully synced ${sobject} (${recordId}) to MySQL, DynamoDB, and S3!`, "success");
    refreshAll();
  } catch (err) {
    showToast(`Sync Error: ${err.message}`, "error");
  }
}

async function loadMySQLRecords() {
  const tableSelect = document.getElementById("mysql-table-select").value;
  const tbody = document.getElementById("mysql-table-body");

  if (!isSalesforceConnected || !getSessionId()) {
    tbody.innerHTML = `<tr><td colspan="6" class="py-12 text-center text-amber-400 font-medium"><div class="flex flex-col items-center justify-center space-y-2"><i class="fa-solid fa-lock text-3xl text-amber-500"></i><span class="text-sm font-semibold">Salesforce Connection Required</span><span class="text-xs text-slate-400">Please connect to Salesforce to view synchronized MySQL database records.</span></div></td></tr>`;
    return;
  }

  tbody.innerHTML = `<tr><td colspan="6" class="py-8 text-center text-slate-500"><i class="fa-solid fa-spinner animate-spin mr-2"></i>Loading MySQL records...</td></tr>`;

  try {
    const res = await fetch(`${API_BASE}/api/db/${tableSelect}`, {
      headers: getAuthHeaders()
    });

    if (res.status === 401) {
      isSalesforceConnected = false;
      renderLockedStateForAllTabs();
      return;
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      tbody.innerHTML = `<tr><td colspan="6" class="py-8 text-center text-amber-400 font-medium"><i class="fa-solid fa-lock mr-2"></i>Salesforce connection required. (${err.detail || "Authentication required"})</td></tr>`;
      return;
    }

    const data = await res.json();
    const records = data.records || data.accounts || data.contacts || data.opportunities || [];

    if (records.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="py-8 text-center text-slate-500">No records found in MySQL table. Click "Sync to AWS & DB" on any Salesforce record to populate.</td></tr>`;
      return;
    }

    tbody.innerHTML = records.map(r => {
      let name = r.name || `${r.firstName || ''} ${r.lastName || ''}`.trim() || "-";
      let attrs = "-";
      if (tableSelect === "accounts") {
        attrs = `Industry: ${r.industry || '-'} | Type: ${r.type || '-'}`;
      } else if (tableSelect === "contacts") {
        attrs = `Email: ${r.email || '-'} | Phone: ${r.phone || '-'}`;
      } else if (tableSelect === "opportunities") {
        attrs = `Stage: ${r.stageName || '-'} | Amount: ${r.amount ? '$' + Number(r.amount).toLocaleString() : '-'}`;
      }
      const syncStatus = r.syncStatus || "SYNCED";
      const updatedAt = r.updatedAt ? new Date(r.updatedAt).toLocaleString() : "N/A";

      return `
        <tr class="hover:bg-slate-800/50 transition">
          <td class="py-3 px-4 font-mono text-xs text-slate-400">#${r.id}</td>
          <td class="py-3 px-4">${renderSalesforceIdLink(r.salesforceId)}</td>
          <td class="py-3 px-4 font-medium text-white">${name}</td>
          <td class="py-3 px-4 text-xs text-slate-300">${attrs}</td>
          <td class="py-3 px-4">
            <span class="bg-emerald-900/60 text-emerald-300 text-xs px-2 py-0.5 rounded border border-emerald-700">${syncStatus}</span>
          </td>
          <td class="py-3 px-4 text-xs text-slate-500">${updatedAt}</td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" class="py-8 text-center text-red-400">Failed to load MySQL records: ${err.message}</td></tr>`;
  }
}

async function loadDynamoDBRecords() {
  const tbody = document.getElementById("dynamodb-table-body");

  if (!isSalesforceConnected || !getSessionId()) {
    tbody.innerHTML = `<tr><td colspan="5" class="py-12 text-center text-amber-400 font-medium"><div class="flex flex-col items-center justify-center space-y-2"><i class="fa-solid fa-lock text-3xl text-amber-500"></i><span class="text-sm font-semibold">Salesforce Connection Required</span><span class="text-xs text-slate-400">Please connect to Salesforce to view AWS DynamoDB items.</span></div></td></tr>`;
    return;
  }

  tbody.innerHTML = `<tr><td colspan="5" class="py-8 text-center text-slate-500"><i class="fa-solid fa-spinner animate-spin mr-2"></i>Scanning DynamoDB...</td></tr>`;

  try {
    const res = await fetch(`${API_BASE}/api/aws/dynamodb/records`, {
      headers: getAuthHeaders()
    });

    if (res.status === 401) {
      isSalesforceConnected = false;
      renderLockedStateForAllTabs();
      return;
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      tbody.innerHTML = `<tr><td colspan="5" class="py-8 text-center text-amber-400 font-medium"><i class="fa-solid fa-lock mr-2"></i>Salesforce connection required. (${err.detail || "Authentication required"})</td></tr>`;
      return;
    }

    const data = await res.json();
    const items = data.records || [];

    if (items.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" class="py-8 text-center text-slate-500">No records found in DynamoDB. Execute a sync first!</td></tr>`;
      return;
    }

    tbody.innerHTML = items.map(item => {
      const payloadStr = JSON.stringify(item.parsedPayload || item.payload || {}, null, 2);
      return `
        <tr class="hover:bg-slate-800/50 transition">
          <td class="py-3 px-4 font-mono text-xs text-amber-400">${item.sObjectType}</td>
          <td class="py-3 px-4">${renderSalesforceIdLink(item.salesforceId)}</td>
          <td class="py-3 px-4">
            <span class="bg-emerald-900/60 text-emerald-300 text-xs px-2 py-0.5 rounded border border-emerald-700">${item.awsSyncStatus || 'SYNCED'}</span>
          </td>
          <td class="py-3 px-4 text-xs text-slate-400">${item.syncedAt ? new Date(item.syncedAt).toLocaleString() : 'N/A'}</td>
          <td class="py-3 px-4">
            <pre class="text-[10px] bg-slate-950 p-2 rounded max-h-20 overflow-y-auto text-slate-300 border border-slate-800">${payloadStr}</pre>
          </td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="5" class="py-8 text-center text-red-400">Failed to load DynamoDB items: ${err.message}</td></tr>`;
  }
}

let currentS3File = null;

async function loadS3Files() {
  const tbody = document.getElementById("s3-table-body");

  if (!isSalesforceConnected || !getSessionId()) {
    tbody.innerHTML = `<tr><td colspan="4" class="py-12 text-center text-amber-400 font-medium"><div class="flex flex-col items-center justify-center space-y-2"><i class="fa-solid fa-lock text-3xl text-amber-500"></i><span class="text-sm font-semibold">Salesforce Connection Required</span><span class="text-xs text-slate-400">Please connect to Salesforce to view AWS S3 event archives.</span></div></td></tr>`;
    return;
  }

  tbody.innerHTML = `<tr><td colspan="4" class="py-8 text-center text-slate-500"><i class="fa-solid fa-spinner animate-spin mr-2"></i>Listing S3 objects...</td></tr>`;

  try {
    const res = await fetch(`${API_BASE}/api/aws/s3/files`, {
      headers: getAuthHeaders()
    });

    if (res.status === 401) {
      isSalesforceConnected = false;
      renderLockedStateForAllTabs();
      return;
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      tbody.innerHTML = `<tr><td colspan="4" class="py-8 text-center text-amber-400 font-medium"><i class="fa-solid fa-lock mr-2"></i>Salesforce connection required. (${err.detail || "Authentication required"})</td></tr>`;
      return;
    }

    const data = await res.json();
    const files = data.files || [];

    if (files.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" class="py-8 text-center text-slate-500">No objects found in S3 bucket. Click "Sync to AWS & DB" on any Salesforce record to archive events.</td></tr>`;
      return;
    }

    const bucketName = data.bucket || "salesforce-raw-events";
    tbody.innerHTML = files.map(f => {
      return `
        <tr class="hover:bg-slate-800/50 transition">
          <td class="py-3 px-4 font-mono text-xs text-emerald-400 flex items-center space-x-2">
            <i class="fa-solid fa-file-code text-slate-500"></i>
            <span class="hover:underline cursor-pointer font-medium" onclick="viewS3File('${f.key}', '${bucketName}')">${f.key}</span>
          </td>
          <td class="py-3 px-4 text-xs text-slate-400">${f.size} bytes</td>
          <td class="py-3 px-4 text-xs text-slate-500">${new Date(f.lastModified).toLocaleString()}</td>
          <td class="py-3 px-4 text-right">
            <button onclick="viewS3File('${f.key}', '${bucketName}')" class="text-xs bg-emerald-950 hover:bg-emerald-900 text-emerald-400 hover:text-emerald-300 border border-emerald-800/80 px-2.5 py-1.5 rounded transition inline-flex items-center space-x-1.5 shadow-sm">
              <i class="fa-solid fa-eye"></i>
              <span>View Content</span>
            </button>
          </td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="4" class="py-8 text-center text-red-400">Failed to load S3 objects: ${err.message}</td></tr>`;
  }
}

async function viewS3File(key, bucket = "salesforce-raw-events") {
  if (!isSalesforceConnected || !getSessionId()) {
    showToast("Please connect to Salesforce first.", "warning");
    return;
  }

  const modal = document.getElementById("s3-viewer-modal");
  const titleEl = document.getElementById("s3-modal-title");
  const bucketEl = document.getElementById("s3-modal-bucket");
  const sizeEl = document.getElementById("s3-modal-size");
  const modEl = document.getElementById("s3-modal-modified");
  const contentEl = document.getElementById("s3-modal-content");

  titleEl.textContent = `s3://${bucket}/${key}`;
  bucketEl.textContent = bucket;
  sizeEl.textContent = "Loading...";
  modEl.textContent = "Loading...";
  contentEl.textContent = "Fetching file content from AWS S3...";

  modal.classList.remove("hidden");

  try {
    const res = await fetch(`${API_BASE}/api/aws/s3/file?key=${encodeURIComponent(key)}&bucket=${encodeURIComponent(bucket)}`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to load S3 file");
    }
    const data = await res.json();
    currentS3File = data;

    sizeEl.textContent = `${data.size} bytes`;
    modEl.textContent = data.lastModified ? new Date(data.lastModified).toLocaleString() : "N/A";

    const displayContent = data.parsedContent ? JSON.stringify(data.parsedContent, null, 2) : (data.rawContent || "Empty file");
    contentEl.textContent = displayContent;
  } catch (err) {
    contentEl.textContent = `Error loading S3 file: ${err.message}`;
  }
}

function closeS3ViewerModal() {
  document.getElementById("s3-viewer-modal").classList.add("hidden");
  currentS3File = null;
}

function copyS3Content() {
  if (!currentS3File) return;
  const content = currentS3File.parsedContent ? JSON.stringify(currentS3File.parsedContent, null, 2) : (currentS3File.rawContent || "");
  navigator.clipboard.writeText(content).then(() => {
    const textEl = document.getElementById("copy-btn-text");
    const orig = textEl.textContent;
    textEl.textContent = "Copied!";
    showToast("File content copied to clipboard!", "success", 2500);
    setTimeout(() => { textEl.textContent = orig; }, 2000);
  }).catch(() => {
    showToast("Failed to copy to clipboard", "error");
  });
}

function downloadS3Content() {
  if (!currentS3File) return;
  const content = currentS3File.parsedContent ? JSON.stringify(currentS3File.parsedContent, null, 2) : (currentS3File.rawContent || "");
  const blob = new Blob([content], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  const fileName = currentS3File.key.split("/").pop() || "s3-event.json";
  a.href = url;
  a.download = fileName;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

async function loadSQSStats() {
  const container = document.getElementById("sqs-cards");

  if (!isSalesforceConnected || !getSessionId()) {
    container.innerHTML = `
      <div class="col-span-2 text-center text-amber-400 py-12 border border-amber-900/40 bg-amber-950/20 rounded-xl space-y-2">
        <i class="fa-solid fa-lock text-3xl text-amber-500"></i>
        <p class="text-sm font-semibold">Salesforce Connection Required</p>
        <p class="text-xs text-slate-400">Please connect to Salesforce to view AWS SQS message queues.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = `<div class="col-span-2 text-center text-slate-500 py-8"><i class="fa-solid fa-spinner animate-spin mr-2"></i>Loading SQS stats...</div>`;

  try {
    const res = await fetch(`${API_BASE}/api/aws/sqs/stats`, {
      headers: getAuthHeaders()
    });

    if (res.status === 401) {
      isSalesforceConnected = false;
      renderLockedStateForAllTabs();
      return;
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      container.innerHTML = `<div class="col-span-2 text-center text-amber-400 py-8"><i class="fa-solid fa-lock mr-2"></i>Salesforce connection required. (${err.detail || "Authentication required"})</div>`;
      return;
    }

    const stats = await res.json();

    container.innerHTML = Object.entries(stats).map(([qName, qData]) => {
      const isDLQ = qName.includes("deadletter");
      return `
        <div class="bg-slate-900 border ${isDLQ ? 'border-red-900/50' : 'border-slate-800'} p-5 rounded-xl space-y-3">
          <div class="flex items-center justify-between">
            <span class="font-mono text-sm font-semibold text-white flex items-center space-x-2">
              <i class="fa-solid fa-envelope ${isDLQ ? 'text-red-400' : 'text-purple-400'}"></i>
              <span>${qName}</span>
            </span>
            <span class="text-xs ${isDLQ ? 'bg-red-900/40 text-red-300 border border-red-800' : 'bg-purple-900/40 text-purple-300 border border-purple-800'} px-2.5 py-0.5 rounded-full">
              ${isDLQ ? 'Dead Letter Queue' : 'Inbound Ingestion'}
            </span>
          </div>
          <div class="grid grid-cols-2 gap-4 pt-2">
            <div class="bg-slate-950 p-3 rounded-lg border border-slate-800/80">
              <span class="text-xs text-slate-400 block">Available Messages</span>
              <span class="text-2xl font-bold text-white">${qData.availableMessages ?? 0}</span>
            </div>
            <div class="bg-slate-950 p-3 rounded-lg border border-slate-800/80">
              <span class="text-xs text-slate-400 block">In-Flight Messages</span>
              <span class="text-2xl font-bold text-slate-300">${qData.inFlightMessages ?? 0}</span>
            </div>
          </div>
        </div>
      `;
    }).join("");
  } catch (err) {
    container.innerHTML = `<div class="col-span-2 text-center text-red-400 py-8">Failed to load SQS queues: ${err.message}</div>`;
  }
}

async function loadSecrets() {
  const tbody = document.getElementById("secrets-table-body");

  if (!isSalesforceConnected || !getSessionId()) {
    tbody.innerHTML = `<tr><td colspan="4" class="py-12 text-center text-amber-400 font-medium"><div class="flex flex-col items-center justify-center space-y-2"><i class="fa-solid fa-lock text-3xl text-amber-500"></i><span class="text-sm font-semibold">Salesforce Connection Required</span><span class="text-xs text-slate-400">Please connect to Salesforce to view AWS Secrets Manager tokens.</span></div></td></tr>`;
    return;
  }

  tbody.innerHTML = `<tr><td colspan="4" class="py-8 text-center text-slate-500"><i class="fa-solid fa-spinner animate-spin mr-2"></i>Querying AWS Secrets Manager...</td></tr>`;

  try {
    const res = await fetch(`${API_BASE}/api/secrets`, {
      headers: getAuthHeaders()
    });

    if (res.status === 401) {
      isSalesforceConnected = false;
      renderLockedStateForAllTabs();
      return;
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      tbody.innerHTML = `<tr><td colspan="4" class="py-8 text-center text-amber-400 font-medium"><i class="fa-solid fa-lock mr-2"></i>Salesforce connection required. (${err.detail || "Authentication required"})</td></tr>`;
      return;
    }

    const data = await res.json();
    const secrets = data.secrets || [];

    if (secrets.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" class="py-8 text-center text-slate-500">No secrets found in Secrets Manager yet. Connect Salesforce via OAuth to store refresh tokens!</td></tr>`;
      return;
    }

    tbody.innerHTML = secrets.map(s => {
      return `
        <tr class="hover:bg-slate-800/50 transition font-mono text-xs">
          <td class="py-3 px-4 text-yellow-400 font-semibold flex items-center space-x-2">
            <i class="fa-solid fa-key text-slate-500"></i>
            <span>${s.name}</span>
          </td>
          <td class="py-3 px-4 text-slate-400 truncate max-w-xs">${s.arn || '-'}</td>
          <td class="py-3 px-4 text-slate-300 font-sans text-xs">${s.description || '-'}</td>
          <td class="py-3 px-4 text-slate-500 font-sans text-xs">${s.lastChangedDate ? new Date(s.lastChangedDate).toLocaleString() : '-'}</td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="4" class="py-8 text-center text-red-400">Failed to load Secrets: ${err.message}</td></tr>`;
  }
}

async function loadLogs() {
  const container = document.getElementById("logs-container");

  if (!isSalesforceConnected || !getSessionId()) {
    container.innerHTML = `
      <div class="text-amber-400 text-center py-12 border border-amber-900/40 bg-amber-950/20 rounded-xl space-y-2">
        <i class="fa-solid fa-lock text-3xl text-amber-500"></i>
        <p class="text-sm font-semibold">Salesforce Connection Required</p>
        <p class="text-xs text-slate-400">Please connect to Salesforce to view integration audit logs.</p>
      </div>
    `;
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/logs`, {
      headers: getAuthHeaders()
    });

    if (res.status === 401) {
      isSalesforceConnected = false;
      renderLockedStateForAllTabs();
      return;
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      container.innerHTML = `<div class="text-amber-400 text-center py-8"><i class="fa-solid fa-lock mr-2"></i>Salesforce connection required. (${err.detail || "Authentication required"})</div>`;
      return;
    }

    const data = await res.json();
    const logs = data.logs || [];

    if (logs.length === 0) {
      container.innerHTML = `<div class="text-slate-500 text-center py-6">No logs recorded yet.</div>`;
      return;
    }

    container.innerHTML = logs.map(l => {
      const isSuccess = l.status === "SUCCESS" || l.status === "PROCESSED";
      const badgeClass = isSuccess ? "bg-emerald-900/50 text-emerald-300 border border-emerald-700" : "bg-red-900/50 text-red-300 border border-red-700";
      return `
        <div class="py-2.5 flex flex-col space-y-1">
          <div class="flex items-center justify-between">
            <span class="font-semibold text-cyan-300">${l.eventType}</span>
            <span class="text-[11px] ${badgeClass} px-2 py-0.5 rounded">${l.status}</span>
          </div>
          <div class="text-[11px] text-slate-400 flex items-center justify-between">
            <span>ID: ${l.id}</span>
            <span>${new Date(l.timestamp).toLocaleTimeString()}</span>
          </div>
          <pre class="bg-slate-950 p-2 rounded text-[11px] text-slate-300 border border-slate-800 mt-1 overflow-x-auto">${JSON.stringify(l.details, null, 2)}</pre>
        </div>
      `;
    }).join("");
  } catch (err) {
    container.innerHTML = `<div class="text-red-400 text-center py-6">Error loading logs: ${err.message}</div>`;
  }
}

async function triggerFullSync() {
  const sessId = getSessionId();
  if (!isSalesforceConnected || !sessId) {
    showToast("Please connect to Salesforce first using the Connect Live Salesforce button.", "warning");
    return;
  }
  const btn = document.getElementById("btn-full-sync");
  btn.disabled = true;
  btn.innerHTML = `<i class="fa-solid fa-spinner animate-spin"></i><span>Syncing in Progress...</span>`;

  try {
    const res = await fetch(`${API_BASE}/api/sync/salesforce-to-aws`, {
      method: "POST",
      headers: getAuthHeaders()
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Full sync failed");
    showToast(`Sync Completed! Synced ${data.summary.synced_count} records to MySQL, DynamoDB, and S3.`, "success");
    refreshAll();
  } catch (err) {
    showToast(`Sync Failed: ${err.message}`, "error");
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<i class="fa-solid fa-play"></i><span>Execute Full Sync Pipeline</span>`;
  }
}

async function triggerAwsToSf() {
  const sessId = getSessionId();
  if (!isSalesforceConnected || !sessId) {
    showToast("Please connect to Salesforce first using the Connect Live Salesforce button.", "warning");
    return;
  }
  const name = document.getElementById("aws-to-sf-name").value;
  const industry = document.getElementById("aws-to-sf-industry").value;

  if (!name) {
    showToast("Please enter an Account Name", "warning");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/sync/aws-to-salesforce`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        sobject: "Account",
        data: {
          Name: name,
          Industry: industry || "Technology",
          Type: "Customer - Channel"
        }
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Push to Salesforce failed");
    showToast(`Record pushed to Live Salesforce! ID: ${data.result.recordId}`, "success");
    document.getElementById("aws-to-sf-name").value = "";
    document.getElementById("aws-to-sf-industry").value = "";
    refreshAll();
  } catch (err) {
    showToast(`Failed to push to Salesforce: ${err.message}`, "error");
  }
}

function openCreateModal() {
  const sessId = getSessionId();
  if (!isSalesforceConnected || !sessId) {
    showToast("Please connect to Salesforce first using the Connect Live Salesforce button.", "warning");
    return;
  }
  document.getElementById("create-modal").classList.remove("hidden");
}

function closeCreateModal() {
  document.getElementById("create-modal").classList.add("hidden");
}

async function submitCreateRecord() {
  const sessId = getSessionId();
  if (!isSalesforceConnected || !sessId) {
    showToast("Please connect to Salesforce first using the Connect Live Salesforce button.", "warning");
    return;
  }
  const sobject = document.getElementById("modal-sobject").value;
  const name = document.getElementById("modal-name").value;
  const extra = document.getElementById("modal-extra").value;

  if (!name) {
    showToast("Please enter a Name", "warning");
    return;
  }

  let payload = {};
  if (sobject === "Account") {
    payload = { Name: name, Industry: extra || "Consulting" };
  } else if (sobject === "Contact") {
    const parts = name.split(" ");
    payload = { FirstName: parts[0], LastName: parts[1] || "Doe", Email: extra || `${parts[0].toLowerCase()}@example.com` };
  } else if (sobject === "Opportunity") {
    payload = { Name: name, StageName: "Prospecting", Amount: Number(extra) || 100000, CloseDate: "2026-12-31" };
  } else if (sobject === "Lead") {
    const parts = name.split(" ");
    payload = { FirstName: parts[0], LastName: parts[1] || "Smith", Company: extra || "Global Enterprises" };
  }

  try {
    const res = await fetch(`${API_BASE}/api/salesforce/records/${sobject}`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Create record failed");
    closeCreateModal();
    showToast(`Record created in Live Salesforce (ID: ${data.id}) and synced to AWS & MySQL!`, "success");
    refreshAll();
  } catch (err) {
    showToast(`Error creating record: ${err.message}`, "error");
  }
}

async function refreshAll() {
  await checkHealth();
  if (!isSalesforceConnected) {
    renderLockedStateForAllTabs();
    return;
  }
  if (currentTab === "salesforce") loadSalesforceRecords();
  if (currentTab === "mysql") loadMySQLRecords();
  if (currentTab === "dynamodb") loadDynamoDBRecords();
  if (currentTab === "s3") loadS3Files();
  if (currentTab === "sqs") loadSQSStats();
  if (currentTab === "secrets") loadSecrets();
  if (currentTab === "admin-mapping") initAdminMappingStudio();
  if (currentTab === "logs") loadLogs();
}

// =============================================================================
// Admin Custom Field Mapping & Query Studio Engine
// =============================================================================
let studioAvailableFields = [];
let studioSelectedFields = new Set();
let studioFieldMappings = {};
let studioLastResult = null;
let studioSavedMappings = [];
let studioCurrentProfileId = null;
let studioMysqlColumns = [];
let studioMysqlTable = "salesforce_accounts";
let studioActiveFieldForModal = "";

function toSnakeCase(str) {
  if (!str) return "";
  return str
    .replace(/([a-z])([A-Z])/g, '$1_$2')
    .replace(/[^a-zA-Z0-9_]/g, '_')
    .toLowerCase()
    .replace(/_+/g, '_')
    .replace(/^_+|_+$/g, '');
}

function initAdminMappingStudio() {
  if (!isSalesforceConnected || !getSessionId()) {
    renderLockedStateForAllTabs();
    return;
  }

  loadCustomMappingsList();

  const resultsSection = document.getElementById("studio-results-section");
  if (studioLastResult) {
    if (resultsSection) resultsSection.classList.remove("hidden");
    renderCustomQueryResultTable(studioLastResult);
  } else {
    if (resultsSection) resultsSection.classList.add("hidden");
  }

  if (studioAvailableFields.length === 0) {
    fetchSobjectSchema();
  }
}

function getSelectedStudioSobject() {
  const select = document.getElementById("studio-sobject-select");
  if (!select) return "Account";
  if (select.value === "custom") {
    const customInput = document.getElementById("studio-custom-sobject-input");
    return (customInput && customInput.value.trim()) ? customInput.value.trim() : "Account";
  }
  return select.value;
}

function onStudioSobjectChange() {
  const select = document.getElementById("studio-sobject-select");
  const customInput = document.getElementById("studio-custom-sobject-input");
  if (select.value === "custom") {
    customInput.classList.remove("hidden");
  } else {
    customInput.classList.add("hidden");
    studioSelectedFields = new Set();
    studioFieldMappings = {};
    fetchSobjectSchema();
  }
}

async function fetchSobjectSchema() {
  const sobject = getSelectedStudioSobject();
  if (!isSalesforceConnected || !getSessionId()) {
    showToast("Please connect to Salesforce first.", "warning");
    return;
  }

  const badge = document.getElementById("schema-fields-badge");
  const btn = document.getElementById("btn-fetch-schema");
  const container = document.getElementById("mapping-fields-container");

  if (badge) badge.textContent = "Fetching...";
  if (btn) btn.innerHTML = `<i class="fa-solid fa-spinner animate-spin"></i><span>Loading...</span>`;
  if (container) container.innerHTML = `<div class="text-slate-400 text-center py-8 text-xs"><i class="fa-solid fa-spinner animate-spin mr-2"></i>Inspecting ${sobject} schema & MySQL table...</div>`;

  try {
    const [sfRes, dbRes] = await Promise.all([
      fetch(`${API_BASE}/api/salesforce/describe/${encodeURIComponent(sobject)}`, { headers: getAuthHeaders() }),
      fetch(`${API_BASE}/api/db/schema-for-sobject/${encodeURIComponent(sobject)}`, { headers: getAuthHeaders() })
    ]);

    if (sfRes.status === 401 || dbRes.status === 401) {
      isSalesforceConnected = false;
      renderLockedStateForAllTabs();
      return;
    }

    if (!sfRes.ok) {
      const err = await sfRes.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to inspect sObject");
    }

    const sfData = await sfRes.json();
    studioAvailableFields = sfData.fields || [];

    if (dbRes.ok) {
      const dbData = await dbRes.json();
      studioMysqlTable = dbData.table_name || `salesforce_${sobject.toLowerCase()}s`;
      studioMysqlColumns = dbData.columns || [];
      const tblBadge = document.getElementById("studio-mysql-table-badge");
      if (tblBadge) {
        tblBadge.textContent = `Table: ${studioMysqlTable} (${studioMysqlColumns.length} cols)`;
      }
    }

    // Pre-select default standard fields if currently empty
    if (studioSelectedFields.size === 0) {
      const defaultPicks = ["Id", "Name", "Type", "Industry", "AnnualRevenue", "BillingCity", "Phone", "Email", "StageName", "Amount", "Status", "CreatedDate"];
      studioAvailableFields.forEach(f => {
        if (defaultPicks.includes(f.name)) {
          studioSelectedFields.add(f.name);
        }
      });
      if (studioSelectedFields.size === 0 && studioAvailableFields.length > 0) {
        studioSelectedFields.add(studioAvailableFields[0].name);
      }
    }

    // Auto-match Salesforce fields to MySQL columns with same name/snake_case name if not yet mapped
    studioAvailableFields.forEach(f => {
      if (!studioFieldMappings[f.name]) {
        const snake = toSnakeCase(f.name);
        const match = studioMysqlColumns.find(c => c.name.toLowerCase() === f.name.toLowerCase() || c.name.toLowerCase() === snake.toLowerCase());
        if (match && match.name.toLowerCase() !== f.name.toLowerCase()) {
          studioFieldMappings[f.name] = match.name;
        }
      }
    });

    if (badge) badge.textContent = `${studioAvailableFields.length} fields found`;
    renderStudioFieldsList();
    showToast(`Loaded ${studioAvailableFields.length} Salesforce fields & ${studioMysqlColumns.length} MySQL columns for ${sobject}!`, "success");
  } catch (err) {
    if (badge) badge.textContent = "Error";
    if (container) container.innerHTML = `<div class="text-red-400 text-center py-6 text-xs">Failed to fetch schema: ${err.message}</div>`;
    showToast(`Describe Error: ${err.message}`, "error");
  } finally {
    if (btn) btn.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i><span>Fetch Schema</span>`;
  }
}

function renderStudioFieldsList(filterText = "") {
  const container = document.getElementById("mapping-fields-container");
  const countBadge = document.getElementById("selected-fields-count");
  if (!container) return;

  if (countBadge) {
    countBadge.textContent = `${studioSelectedFields.size} of ${studioAvailableFields.length} selected`;
  }

  if (studioAvailableFields.length === 0) {
    container.innerHTML = `<div class="text-slate-500 text-center py-8 text-xs">No fields available. Click "Fetch Schema" to load fields.</div>`;
    return;
  }

  const query = (filterText || "").toLowerCase().trim();
  const filtered = studioAvailableFields.filter(f => 
    !query || f.name.toLowerCase().includes(query) || (f.label && f.label.toLowerCase().includes(query))
  );

  if (filtered.length === 0) {
    container.innerHTML = `<div class="text-slate-500 text-center py-6 text-xs">No fields matching "${filterText}"</div>`;
    return;
  }

  const typeColorMap = {
    id: "bg-blue-900/60 text-blue-300 border-blue-700",
    string: "bg-slate-800 text-slate-300 border-slate-700",
    picklist: "bg-purple-900/60 text-purple-300 border-purple-700",
    currency: "bg-emerald-900/60 text-emerald-300 border-emerald-700",
    date: "bg-amber-900/60 text-amber-300 border-amber-700",
    datetime: "bg-amber-900/60 text-amber-300 border-amber-700",
    boolean: "bg-cyan-900/60 text-cyan-300 border-cyan-700",
    reference: "bg-indigo-900/60 text-indigo-300 border-indigo-700",
    textarea: "bg-slate-800 text-slate-300 border-slate-700"
  };

  const sortedMysqlCols = [...studioMysqlColumns].sort((a, b) => a.name.localeCompare(b.name));

  container.innerHTML = filtered.map(f => {
    const isChecked = studioSelectedFields.has(f.name);
    const currentAlias = studioFieldMappings[f.name] || "";
    const typeBadge = typeColorMap[f.type] || "bg-slate-800 text-slate-400 border-slate-700";

    const isMysqlCol = studioMysqlColumns.some(c => c.name.toLowerCase() === currentAlias.toLowerCase());

    return `
      <div class="flex items-center justify-between gap-4 p-2.5 hover:bg-slate-900/90 rounded-lg transition group border border-transparent hover:border-slate-800/80">
        <label class="flex items-center space-x-3 cursor-pointer flex-1 min-w-0 pr-2">
          <input type="checkbox" onchange="toggleStudioField('${f.name}', this.checked)" ${isChecked ? 'checked' : ''} class="w-4 h-4 rounded bg-slate-800 border-slate-700 text-indigo-600 focus:ring-0 cursor-pointer flex-shrink-0">
          <div class="truncate">
            <span class="text-xs font-semibold ${isChecked ? 'text-white' : 'text-slate-400'} group-hover:text-white block truncate">${f.label || f.name}</span>
            <span class="font-mono text-[11px] text-slate-500 block truncate">${f.name}</span>
          </div>
          <span class="text-[9px] px-1.5 py-0.5 rounded border ${typeBadge} uppercase font-mono font-medium flex-shrink-0">${f.type}</span>
          ${f.custom ? '<span class="text-[9px] px-1.5 bg-amber-950 text-amber-400 rounded border border-amber-800 font-semibold flex-shrink-0">custom</span>' : ''}
        </label>
        
        <div class="w-72 sm:w-80 md:w-96 flex-shrink-0">
          <select onchange="handleStudioFieldTargetChange('${f.name}', this.value)" class="w-full bg-slate-950 border border-slate-700/80 hover:border-indigo-500/80 focus:border-indigo-500 text-xs text-indigo-300 px-3 py-2 rounded-lg focus:outline-none font-mono cursor-pointer shadow-inner">
            <option value="">⚙️ Default (${f.name})</option>
            ${currentAlias && !isMysqlCol ? `<option value="${currentAlias}" selected>✏️ Custom: ${currentAlias}</option>` : ''}
            <optgroup label="── 🗄️ MySQL Columns (${studioMysqlTable}) ──">
              ${sortedMysqlCols.map(c => `
                <option value="${c.name}" ${(currentAlias.toLowerCase() === c.name.toLowerCase() || (!currentAlias && f.name.toLowerCase() === c.name.toLowerCase())) ? 'selected' : ''}>
                  🔹 ${c.name} (${c.type})
                </option>
              `).join("")}
            </optgroup>
            <optgroup label="── ⚡ Database Actions ──">
              <option value="__ADD_NEW_MYSQL_COL__">➕ + Add New Field to MySQL...</option>
              <option value="__ENTER_CUSTOM_ALIAS__">✏️ Enter Custom Alias...</option>
            </optgroup>
          </select>
        </div>
      </div>
    `;
  }).join("");
}

function handleStudioFieldTargetChange(fieldName, value) {
  if (value === "__ADD_NEW_MYSQL_COL__") {
    openAddMysqlColumnModal(fieldName);
    renderStudioFieldsList(document.getElementById("mapping-field-search").value);
    return;
  }
  if (value === "__ENTER_CUSTOM_ALIAS__") {
    const existing = studioFieldMappings[fieldName] || fieldName;
    const custom = prompt(`Enter custom target column alias for '${fieldName}':`, existing);
    if (custom !== null && custom.trim() !== "") {
      studioFieldMappings[fieldName] = custom.trim();
      studioSelectedFields.add(fieldName);
    }
    renderStudioFieldsList(document.getElementById("mapping-field-search").value);
    return;
  }
  if (!value || value.trim() === "") {
    delete studioFieldMappings[fieldName];
  } else {
    studioFieldMappings[fieldName] = value.trim();
    studioSelectedFields.add(fieldName);
  }
  renderStudioFieldsList(document.getElementById("mapping-field-search").value);
}

function openAddMysqlColumnModal(fieldName = "") {
  const modal = document.getElementById("add-mysql-column-modal");
  if (!modal) return;

  studioActiveFieldForModal = fieldName || "";
  document.getElementById("modal-mysql-table-name").value = studioMysqlTable;
  
  const initialName = fieldName ? toSnakeCase(fieldName) : "";
  document.getElementById("modal-new-column-name").value = initialName;
  updateModalColPreview();

  const autoMapContainer = document.getElementById("modal-auto-map-container");
  const autoMapField = document.getElementById("modal-auto-map-field");
  const autoMapCheck = document.getElementById("modal-auto-map-check");

  if (fieldName) {
    if (autoMapContainer) autoMapContainer.classList.remove("hidden");
    if (autoMapField) autoMapField.textContent = fieldName;
    if (autoMapCheck) autoMapCheck.checked = true;
  } else {
    if (autoMapContainer) autoMapContainer.classList.add("hidden");
    if (autoMapCheck) autoMapCheck.checked = false;
  }

  modal.classList.remove("hidden");
  document.getElementById("modal-new-column-name").focus();
}

function closeAddMysqlColumnModal() {
  const modal = document.getElementById("add-mysql-column-modal");
  if (modal) modal.classList.add("hidden");
  studioActiveFieldForModal = "";
}

function updateModalColPreview() {
  const val = document.getElementById("modal-new-column-name").value;
  const preview = document.getElementById("modal-col-preview");
  if (preview) {
    preview.textContent = val ? toSnakeCase(val) : "-";
  }
}

async function submitAddNewMysqlColumn() {
  const rawName = document.getElementById("modal-new-column-name").value;
  const colName = toSnakeCase(rawName);
  const dataType = document.getElementById("modal-new-column-type").value;
  const sobject = getSelectedStudioSobject();

  if (!colName) {
    showToast("Please enter a valid column name", "warning");
    return;
  }

  const btn = document.getElementById("btn-submit-add-column");
  btn.disabled = true;
  btn.innerHTML = `<i class="fa-solid fa-spinner animate-spin"></i><span>Adding Column...</span>`;

  try {
    const res = await fetch(`${API_BASE}/api/db/add-column`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        sobject,
        table_name: studioMysqlTable,
        column_name: colName,
        data_type: dataType
      })
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to add column");
    }

    const data = await res.json();
    studioMysqlColumns = data.columns || [];
    studioMysqlTable = data.table_name || studioMysqlTable;

    const autoMapCheck = document.getElementById("modal-auto-map-check");
    if (autoMapCheck && autoMapCheck.checked && studioActiveFieldForModal) {
      studioFieldMappings[studioActiveFieldForModal] = data.column_name;
      studioSelectedFields.add(studioActiveFieldForModal);
    }

    closeAddMysqlColumnModal();
    renderStudioFieldsList();
    showToast(`Column '${data.column_name}' (${dataType}) added to MySQL table '${studioMysqlTable}'!`, "success");
  } catch (err) {
    showToast(`Database Error: ${err.message}`, "error");
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<i class="fa-solid fa-plus"></i><span>Add Column to Table</span>`;
  }
}

function filterStudioFieldsList() {
  const val = document.getElementById("mapping-field-search").value;
  renderStudioFieldsList(val);
}

function toggleStudioField(fieldName, isChecked) {
  if (isChecked) {
    studioSelectedFields.add(fieldName);
  } else {
    studioSelectedFields.delete(fieldName);
  }
  const countBadge = document.getElementById("selected-fields-count");
  if (countBadge) {
    countBadge.textContent = `${studioSelectedFields.size} of ${studioAvailableFields.length} selected`;
  }
}

function updateStudioFieldAlias(fieldName, alias) {
  if (alias && alias.trim()) {
    studioFieldMappings[fieldName] = alias.trim();
  } else {
    delete studioFieldMappings[fieldName];
  }
}

function selectAllStudioFields(select) {
  if (select) {
    studioAvailableFields.forEach(f => studioSelectedFields.add(f.name));
  } else {
    studioSelectedFields.clear();
  }
  const filterVal = document.getElementById("mapping-field-search").value;
  renderStudioFieldsList(filterVal);
}

async function executeStudioCustomQuery() {
  if (!isSalesforceConnected || !getSessionId()) {
    showToast("Please connect to Salesforce first.", "warning");
    return;
  }

  const sobject = getSelectedStudioSobject();
  const fields = Array.from(studioSelectedFields);

  if (fields.length === 0) {
    showToast("Please select at least one field to query.", "warning");
    return;
  }

  const filterClause = document.getElementById("studio-filter-clause").value.trim() || null;
  const sortField = document.getElementById("studio-sort-field").value.trim() || null;
  const sortOrder = document.getElementById("studio-sort-order").value;
  const recordLimit = parseInt(document.getElementById("studio-record-limit").value, 10) || 50;

  const btn = document.getElementById("btn-execute-custom-query");
  btn.disabled = true;
  btn.innerHTML = `<i class="fa-solid fa-spinner animate-spin"></i><span>Executing SOQL & Pulling Data...</span>`;

  const tbody = document.getElementById("custom-query-tbody");
  tbody.innerHTML = `<tr><td colspan="10" class="py-16 text-center text-slate-400"><i class="fa-solid fa-spinner animate-spin text-2xl text-indigo-400 block mb-2"></i>Querying Live Salesforce...</td></tr>`;

  try {
    const payload = {
      sobject,
      fields,
      mappings: studioFieldMappings,
      filter_clause: filterClause,
      sort_field: sortField,
      sort_order: sortOrder,
      record_limit: recordLimit
    };

    const res = await fetch(`${API_BASE}/api/salesforce/custom-query`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    });

    if (res.status === 401) {
      isSalesforceConnected = false;
      renderLockedStateForAllTabs();
      return;
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Query execution failed");
    }

    const data = await res.json();
    studioLastResult = data;

    // Reveal on-demand results section and smooth scroll
    const resultsSection = document.getElementById("studio-results-section");
    if (resultsSection) {
      resultsSection.classList.remove("hidden");
      setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 100);
    }

    // Show SOQL bar
    const soqlBar = document.getElementById("custom-soql-bar");
    const soqlText = document.getElementById("custom-soql-text");
    if (soqlBar && soqlText) {
      soqlText.textContent = data.soql;
      soqlBar.classList.remove("hidden");
    }

    const countBadge = document.getElementById("custom-query-count-badge");
    if (countBadge) {
      countBadge.textContent = `${data.total} records pulled`;
    }

    renderCustomQueryResultTable(data);
    
    // Update raw JSON
    const rawPre = document.getElementById("custom-query-raw-json");
    if (rawPre) {
      rawPre.textContent = JSON.stringify(data, null, 2);
    }

    showToast(`Successfully pulled ${data.total} records from Salesforce!`, "success");
  } catch (err) {
    const resultsSection = document.getElementById("studio-results-section");
    if (resultsSection) {
      resultsSection.classList.remove("hidden");
      resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    tbody.innerHTML = `<tr><td colspan="10" class="py-12 text-center text-red-400"><i class="fa-solid fa-triangle-exclamation text-2xl mb-2 text-red-500 block"></i>Query Execution Error: ${err.message}</td></tr>`;
    showToast(`Query Error: ${err.message}`, "error");
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<i class="fa-solid fa-play"></i><span>Execute & Pull Live Data</span>`;
  }
}

function closeStudioResultsSection() {
  const resultsSection = document.getElementById("studio-results-section");
  if (resultsSection) {
    resultsSection.classList.add("hidden");
  }
}

function renderCustomQueryResultTable(data) {
  const thead = document.getElementById("custom-query-thead");
  const tbody = document.getElementById("custom-query-tbody");
  if (!thead || !tbody) return;

  const records = data.records || [];
  if (records.length === 0) {
    tbody.innerHTML = `<tr><td colspan="10" class="py-12 text-center text-slate-500">No records returned matching your query criteria.</td></tr>`;
    return;
  }

  // Determine headers from mappings or fields
  const fields = data.fields || [];
  const mappings = data.mappings || {};

  const headers = fields.map(f => {
    const alias = mappings[f] || f;
    const isMapped = alias !== f;
    return `
      <th class="py-3 px-4 font-semibold whitespace-nowrap">
        <div class="flex flex-col">
          <span class="text-white">${alias}</span>
          ${isMapped ? `<span class="text-[9px] font-mono text-slate-500 lowercase">(${f})</span>` : ''}
        </div>
      </th>
    `;
  }).join("");

  thead.innerHTML = `<tr>${headers}</tr>`;

  tbody.innerHTML = records.map(r => {
    const raw = r._raw || {};
    const cells = fields.map(f => {
      let val = raw[f];
      if (f.toLowerCase() === "id" && val) {
        return `<td class="py-3 px-4">${renderSalesforceIdLink(val)}</td>`;
      }
      if (val === null || val === undefined) {
        return `<td class="py-3 px-4 font-mono text-xs text-slate-600">-</td>`;
      }
      if (typeof val === "boolean") {
        return `<td class="py-3 px-4"><span class="px-1.5 py-0.5 rounded text-[10px] font-mono ${val ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-slate-800 text-slate-400'}">${val}</span></td>`;
      }
      if (typeof val === "object") {
        val = JSON.stringify(val);
      }
      return `<td class="py-3 px-4 text-xs text-slate-300 truncate max-w-xs" title="${String(val)}">${String(val)}</td>`;
    }).join("");

    return `<tr class="hover:bg-slate-800/50 transition">${cells}</tr>`;
  }).join("");
}

function switchStudioResultView(mode) {
  const tableWrapper = document.getElementById("studio-table-wrapper");
  const rawWrapper = document.getElementById("studio-raw-wrapper");
  const btnTable = document.getElementById("btn-view-table");
  const btnRaw = document.getElementById("btn-view-raw");

  if (mode === "raw") {
    if (tableWrapper) tableWrapper.classList.add("hidden");
    if (rawWrapper) rawWrapper.classList.remove("hidden");
    if (btnTable) { btnTable.className = "px-2.5 py-1 rounded text-slate-400 hover:text-white text-[11px] transition"; }
    if (btnRaw) { btnRaw.className = "px-2.5 py-1 rounded bg-indigo-600 text-white font-medium text-[11px] transition"; }
  } else {
    if (tableWrapper) tableWrapper.classList.remove("hidden");
    if (rawWrapper) rawWrapper.classList.add("hidden");
    if (btnTable) { btnTable.className = "px-2.5 py-1 rounded bg-indigo-600 text-white font-medium text-[11px] transition"; }
    if (btnRaw) { btnRaw.className = "px-2.5 py-1 rounded text-slate-400 hover:text-white text-[11px] transition"; }
  }
}

function copyExecutedSoql() {
  const soql = document.getElementById("custom-soql-text").textContent;
  if (!soql) return;
  navigator.clipboard.writeText(soql).then(() => {
    const textEl = document.getElementById("copy-soql-text");
    const orig = textEl.textContent;
    textEl.textContent = "Copied!";
    showToast("SOQL query copied to clipboard!", "success", 2000);
    setTimeout(() => { textEl.textContent = orig; }, 2000);
  });
}

function exportCustomQueryResult(format) {
  if (!studioLastResult || !studioLastResult.records || studioLastResult.records.length === 0) {
    showToast("No records available to export. Run a query first!", "warning");
    return;
  }

  const sobject = studioLastResult.sobject || "SalesforceExport";
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-");

  if (format === "json") {
    const mappedData = studioLastResult.records.map(r => r._mapped || r._raw);
    const jsonStr = JSON.stringify(mappedData, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${sobject}-mapped-export-${timestamp}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast("Exported JSON successfully!", "success");
  } else if (format === "csv") {
    const records = studioLastResult.records.map(r => r._mapped || r._raw);
    const headers = Object.keys(records[0] || {});
    
    const csvRows = [];
    csvRows.push(headers.map(h => `"${h.replace(/"/g, '""')}"`).join(","));
    
    for (const r of records) {
      const values = headers.map(h => {
        const val = r[h] === null || r[h] === undefined ? "" : String(r[h]);
        return `"${val.replace(/"/g, '""')}"`;
      });
      csvRows.push(values.join(","));
    }

    const csvContent = csvRows.join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${sobject}-mapped-export-${timestamp}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    showToast("Exported CSV successfully!", "success");
  }
}

async function loadCustomMappingsList() {
  if (!isSalesforceConnected || !getSessionId()) return;

  try {
    const res = await fetch(`${API_BASE}/api/admin/mappings`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) return;

    const data = await res.json();
    studioSavedMappings = data.mappings || [];

    const select = document.getElementById("mapping-profile-select");
    if (!select) return;

    select.innerHTML = `<option value="">-- Choose or Create Profile (${studioSavedMappings.length} saved) --</option>` +
      studioSavedMappings.map(m => `
        <option value="${m.id}">${m.name} (${m.sobject} - ${m.selected_fields.length} fields)</option>
      `).join("");
  } catch (err) {
    console.error("Failed to load custom mappings:", err);
  }
}

function onMappingProfileSelected() {
  const select = document.getElementById("mapping-profile-select");
  const profileId = parseInt(select.value, 10);

  const btnUpdate = document.getElementById("btn-update-profile");
  const btnDelete = document.getElementById("btn-delete-profile");

  if (!profileId) {
    studioCurrentProfileId = null;
    if (btnUpdate) btnUpdate.classList.add("hidden");
    if (btnDelete) btnDelete.classList.add("hidden");
    return;
  }

  const profile = studioSavedMappings.find(m => m.id === profileId);
  if (!profile) return;

  studioCurrentProfileId = profile.id;
  document.getElementById("mapping-profile-name").value = profile.name;

  // Set sobject
  const sfSelect = document.getElementById("studio-sobject-select");
  const customInput = document.getElementById("studio-custom-sobject-input");
  const standardValues = ["Account", "Contact", "Opportunity", "Lead", "Case", "User", "Task"];
  if (standardValues.includes(profile.sobject)) {
    sfSelect.value = profile.sobject;
    customInput.classList.add("hidden");
  } else {
    sfSelect.value = "custom";
    customInput.value = profile.sobject;
    customInput.classList.remove("hidden");
  }

  // Set preferences
  document.getElementById("studio-filter-clause").value = profile.filter_clause || "";
  document.getElementById("studio-sort-field").value = profile.sort_field || "";
  document.getElementById("studio-sort-order").value = profile.sort_order || "DESC";
  document.getElementById("studio-record-limit").value = String(profile.record_limit || 50);

  // Set selected fields & mappings
  studioSelectedFields = new Set(profile.selected_fields || []);
  studioFieldMappings = { ...(profile.field_mappings || {}) };

  if (btnUpdate) btnUpdate.classList.remove("hidden");
  if (btnDelete) btnDelete.classList.remove("hidden");

  fetchSobjectSchema().then(() => {
    showToast(`Loaded mapping profile '${profile.name}'`, "info");
  });
}

async function saveCurrentMappingProfile(isUpdate = false) {
  if (!isSalesforceConnected || !getSessionId()) {
    showToast("Please connect to Salesforce first.", "warning");
    return;
  }

  const name = document.getElementById("mapping-profile-name").value.trim();
  if (!name) {
    showToast("Please provide a name for this mapping profile.", "warning");
    return;
  }

  const sobject = getSelectedStudioSobject();
  const selected_fields = Array.from(studioSelectedFields);
  if (selected_fields.length === 0) {
    showToast("Please select at least one field.", "warning");
    return;
  }

  const payload = {
    name,
    sobject,
    selected_fields,
    field_mappings: studioFieldMappings,
    filter_clause: document.getElementById("studio-filter-clause").value.trim() || null,
    sort_field: document.getElementById("studio-sort-field").value.trim() || null,
    sort_order: document.getElementById("studio-sort-order").value,
    record_limit: parseInt(document.getElementById("studio-record-limit").value, 10) || 50
  };

  try {
    const url = isUpdate && studioCurrentProfileId ? `${API_BASE}/api/admin/mappings/${studioCurrentProfileId}` : `${API_BASE}/api/admin/mappings`;
    const method = isUpdate && studioCurrentProfileId ? "PUT" : "POST";

    const res = await fetch(url, {
      method,
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to save profile");
    }

    const data = await res.json();
    showToast(data.message || `Profile '${name}' saved successfully!`, "success");
    await loadCustomMappingsList();
  } catch (err) {
    showToast(`Save Error: ${err.message}`, "error");
  }
}

async function deleteCurrentMappingProfile() {
  if (!studioCurrentProfileId) return;
  if (!confirm("Are you sure you want to delete this custom mapping profile?")) return;

  try {
    const res = await fetch(`${API_BASE}/api/admin/mappings/${studioCurrentProfileId}`, {
      method: "DELETE",
      headers: getAuthHeaders()
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to delete");
    }
    showToast("Mapping profile deleted successfully", "success");
    resetMappingStudioForm();
    await loadCustomMappingsList();
  } catch (err) {
    showToast(`Delete Error: ${err.message}`, "error");
  }
}

function resetMappingStudioForm() {
  studioCurrentProfileId = null;
  document.getElementById("mapping-profile-select").value = "";
  document.getElementById("mapping-profile-name").value = "";
  document.getElementById("studio-filter-clause").value = "";
  document.getElementById("studio-sort-field").value = "";
  document.getElementById("studio-record-limit").value = "50";
  
  const btnUpdate = document.getElementById("btn-update-profile");
  const btnDelete = document.getElementById("btn-delete-profile");
  if (btnUpdate) btnUpdate.classList.add("hidden");
  if (btnDelete) btnDelete.classList.add("hidden");
}

// Initial Boot
window.addEventListener("DOMContentLoaded", async () => {
  renderLockedStateForAllTabs();
  handleOAuthParams();
  await refreshAll();
  setInterval(checkHealth, 15000);
});
