const API_BASE = "http://localhost:8000";

let currentTab = "salesforce";

function switchTab(tabId) {
  currentTab = tabId;
  ["salesforce", "dynamodb", "s3", "sqs", "sync", "logs"].forEach(t => {
    const el = document.getElementById(`tab-${t}`);
    const btn = document.getElementById(`tab-btn-${t}`);
    if (el) el.classList.toggle("hidden", t !== tabId);
    if (btn) btn.classList.toggle("tab-active", t === tabId);
  });

  if (tabId === "salesforce") loadSalesforceRecords();
  if (tabId === "dynamodb") loadDynamoDBRecords();
  if (tabId === "s3") loadS3Files();
  if (tabId === "sqs") loadSQSStats();
  if (tabId === "logs") loadLogs();
}

async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/api/status`);
    const data = await res.json();
    
    // SF Health Badge
    const sfEl = document.getElementById("sf-health");
    if (data.salesforce && data.salesforce.status === "connected") {
      sfEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-400"></span><span class="text-emerald-300">Live Salesforce: Connected</span>`;
    } else {
      sfEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-400"></span><span class="text-amber-300">Live Salesforce: Check Credentials</span>`;
    }

    // AWS Health Badge
    const awsEl = document.getElementById("aws-health");
    if (data.aws && data.aws.status === "connected") {
      awsEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-400"></span><span class="text-emerald-300">AWS: LocalStack Online</span>`;
    } else {
      awsEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-red-400"></span><span class="text-red-300">AWS: Offline</span>`;
    }

    // Update log count
    document.getElementById("log-count").textContent = data.recentLogsCount || 0;
  } catch (err) {
    console.error("Health check error:", err);
  }
}

async function loadSalesforceRecords() {
  const sobject = document.getElementById("sf-object-select").value;
  const tbody = document.getElementById("sf-table-body");
  tbody.innerHTML = `<tr><td colspan="5" class="py-8 text-center text-slate-500">Loading ${sobject}s from Live Salesforce...</td></tr>`;

  try {
    const res = await fetch(`${API_BASE}/api/salesforce/records/${sobject}`);
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
          <td class="py-3 px-4 font-mono text-xs text-blue-400">${r.Id}</td>
          <td class="py-3 px-4 font-medium text-white">${name}</td>
          <td class="py-3 px-4 text-xs text-slate-400">${extra}</td>
          <td class="py-3 px-4 text-xs text-slate-500">${modDate}</td>
          <td class="py-3 px-4 text-right">
            <button onclick="syncSingleRecord('${sobject}', '${r.Id}')" class="text-xs bg-slate-800 hover:bg-slate-700 text-cyan-400 px-2.5 py-1 rounded border border-slate-700">
              <i class="fa-solid fa-cloud-arrow-up mr-1"></i> Sync to AWS
            </button>
          </td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="5" class="py-8 text-center text-red-400">Failed to load records from Live Salesforce: ${err.message}. Please verify .env credentials.</td></tr>`;
  }
}

async function loadDynamoDBRecords() {
  const tbody = document.getElementById("dynamodb-table-body");
  tbody.innerHTML = `<tr><td colspan="5" class="py-8 text-center text-slate-500">Scanning DynamoDB...</td></tr>`;

  try {
    const res = await fetch(`${API_BASE}/api/aws/dynamodb/records`);
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
          <td class="py-3 px-4 font-mono text-xs text-blue-400">${item.salesforceId}</td>
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

async function loadS3Files() {
  const tbody = document.getElementById("s3-table-body");
  tbody.innerHTML = `<tr><td colspan="3" class="py-8 text-center text-slate-500">Listing S3 objects...</td></tr>`;

  try {
    const res = await fetch(`${API_BASE}/api/aws/s3/files`);
    const data = await res.json();
    const files = data.files || [];

    if (files.length === 0) {
      tbody.innerHTML = `<tr><td colspan="3" class="py-8 text-center text-slate-500">No objects found in S3 bucket.</td></tr>`;
      return;
    }

    tbody.innerHTML = files.map(f => {
      return `
        <tr class="hover:bg-slate-800/50 transition">
          <td class="py-3 px-4 font-mono text-xs text-emerald-400 flex items-center space-x-2">
            <i class="fa-solid fa-file-code text-slate-500"></i>
            <span>${f.key}</span>
          </td>
          <td class="py-3 px-4 text-xs text-slate-400">${f.size} bytes</td>
          <td class="py-3 px-4 text-xs text-slate-500">${new Date(f.lastModified).toLocaleString()}</td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="3" class="py-8 text-center text-red-400">Failed to load S3 objects: ${err.message}</td></tr>`;
  }
}

async function loadSQSStats() {
  const container = document.getElementById("sqs-cards");
  container.innerHTML = `<div class="col-span-2 text-center text-slate-500 py-8">Loading SQS stats...</div>`;

  try {
    const res = await fetch(`${API_BASE}/api/aws/sqs/stats`);
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

async function loadLogs() {
  const container = document.getElementById("logs-container");
  try {
    const res = await fetch(`${API_BASE}/api/logs`);
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
  const btn = document.getElementById("btn-full-sync");
  btn.disabled = true;
  btn.innerHTML = `<i class="fa-solid fa-spinner animate-spin"></i><span>Syncing in Progress...</span>`;

  try {
    const res = await fetch(`${API_BASE}/api/sync/salesforce-to-aws`, { method: "POST" });
    const data = await res.json();
    alert(`Sync Completed! Synced ${data.summary.synced_count} records from Live Salesforce to DynamoDB and S3.`);
    refreshAll();
  } catch (err) {
    alert(`Sync Failed: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<i class="fa-solid fa-play"></i><span>Execute Full Sync Pipeline</span>`;
  }
}

async function triggerAwsToSf() {
  const name = document.getElementById("aws-to-sf-name").value;
  const industry = document.getElementById("aws-to-sf-industry").value;

  if (!name) {
    alert("Please enter an Account Name");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/sync/aws-to-salesforce`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
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
    alert(`Record pushed to Live Salesforce! ID: ${data.result.recordId}`);
    document.getElementById("aws-to-sf-name").value = "";
    document.getElementById("aws-to-sf-industry").value = "";
    refreshAll();
  } catch (err) {
    alert(`Failed to push to Salesforce: ${err.message}`);
  }
}

function openCreateModal() {
  document.getElementById("create-modal").classList.remove("hidden");
}

function closeCreateModal() {
  document.getElementById("create-modal").classList.add("hidden");
}

async function submitCreateRecord() {
  const sobject = document.getElementById("modal-sobject").value;
  const name = document.getElementById("modal-name").value;
  const extra = document.getElementById("modal-extra").value;

  if (!name) {
    alert("Please enter a Name");
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
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    closeCreateModal();
    alert(`Record created in Live Salesforce (ID: ${data.id}) and synced to AWS!`);
    refreshAll();
  } catch (err) {
    alert(`Error creating record: ${err.message}`);
  }
}

function refreshAll() {
  checkHealth();
  if (currentTab === "salesforce") loadSalesforceRecords();
  if (currentTab === "dynamodb") loadDynamoDBRecords();
  if (currentTab === "s3") loadS3Files();
  if (currentTab === "sqs") loadSQSStats();
  if (currentTab === "logs") loadLogs();
}

// Initial Boot
window.addEventListener("DOMContentLoaded", () => {
  checkHealth();
  loadSalesforceRecords();
  setInterval(checkHealth, 10000);
});
