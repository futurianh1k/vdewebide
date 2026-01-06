function qs(sel) { return document.querySelector(sel); }

const state = {
  view: "workspaces",
  adminKey: "",
};

function setView(name) {
  state.view = name;
  document.querySelectorAll(".nav-item").forEach((b) => b.classList.toggle("active", b.dataset.view === name));
  qs("#view-workspaces").classList.toggle("hidden", name !== "workspaces");
  qs("#view-gateway").classList.toggle("hidden", name !== "gateway");
  qs("#pageTitle").textContent = name === "workspaces" ? "Workspaces" : "Gateway Test";
  qs("#pageDesc").textContent = name === "workspaces"
    ? "code-server + opencode 컨셉의 워크스페이스를 관리합니다."
    : "관리자 화면에서 AI Gateway 호출을 빠르게 점검합니다(데모).";
}

async function api(path, opts = {}) {
  const headers = Object.assign({}, opts.headers || {});
  if (state.adminKey) headers["X-Admin-Key"] = state.adminKey;
  if (!headers["Content-Type"] && opts.body) headers["Content-Type"] = "application/json";
  const r = await fetch(path, Object.assign({}, opts, { headers }));
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(JSON.stringify(data));
  return data;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[c]));
}

function wsRow(ws) {
  const url = ws.url ? `<a class="link" href="${escapeHtml(ws.url)}" target="_blank" rel="noreferrer">${escapeHtml(ws.url)}</a>` : "-";
  return `
    <tr>
      <td><code>${escapeHtml(ws.id)}</code></td>
      <td>${escapeHtml(ws.name)}</td>
      <td>${escapeHtml(ws.owner_user_id)}</td>
      <td>${escapeHtml(ws.project_id)}</td>
      <td><span class="badge">${escapeHtml(ws.status)}</span></td>
      <td>${url}</td>
      <td class="row">
        <button class="btn" data-action="start" data-id="${escapeHtml(ws.id)}">Start</button>
        <button class="btn" data-action="stop" data-id="${escapeHtml(ws.id)}">Stop</button>
        <button class="btn" data-action="delete" data-id="${escapeHtml(ws.id)}">Delete</button>
      </td>
    </tr>
  `;
}

async function refreshWorkspaces() {
  const res = await api("/api/workspaces");
  const rows = (res.items || []).map(wsRow).join("");
  qs("#wsTbody").innerHTML = rows || `<tr><td colspan="7" style="color:rgba(255,255,255,0.6);">no workspaces</td></tr>`;
}

async function onCreate() {
  const name = qs("#wsName").value.trim();
  const owner = (qs("#wsOwner").value.trim() || "dev-user");
  const project = (qs("#wsProject").value.trim() || "dev-project");
  if (!name) return alert("Workspace name is required");
  await api("/api/workspaces", { method: "POST", body: JSON.stringify({ name, owner_user_id: owner, project_id: project }) });
  qs("#wsName").value = "";
  await refreshWorkspaces();
}

async function onWsAction(e) {
  const btn = e.target.closest("button");
  if (!btn) return;
  const action = btn.dataset.action;
  const id = btn.dataset.id;
  if (!action || !id) return;
  if (action === "delete" && !confirm(`Delete workspace ${id}?`)) return;

  if (action === "start") await api(`/api/workspaces/${id}/start`, { method: "POST" });
  if (action === "stop") await api(`/api/workspaces/${id}/stop`, { method: "POST" });
  if (action === "delete") await api(`/api/workspaces/${id}`, { method: "DELETE" });
  await refreshWorkspaces();
}

async function onGatewaySend() {
  const path = qs("#gwPath").value.trim();
  const auth = qs("#gwAuth").value.trim();
  const bodyText = qs("#gwBody").value;
  qs("#gwOut").textContent = "loading...";
  const headers = {};
  if (auth) headers["Authorization"] = auth;
  const data = await api(`/api/gateway/${path}`, { method: "POST", headers, body: bodyText });
  qs("#gwOut").textContent = JSON.stringify(data, null, 2);
}

function init() {
  document.querySelectorAll(".nav-item").forEach((b) => b.addEventListener("click", () => setView(b.dataset.view)));
  qs("#refreshBtn").addEventListener("click", () => refreshWorkspaces().catch((e) => alert(e.message)));
  qs("#createBtn").addEventListener("click", () => onCreate().catch((e) => alert(e.message)));
  qs("#wsTbody").addEventListener("click", (e) => onWsAction(e).catch((err) => alert(err.message)));
  qs("#gwSendBtn").addEventListener("click", () => onGatewaySend().catch((e) => alert(e.message)));
  qs("#adminKey").addEventListener("input", (e) => { state.adminKey = e.target.value; });

  setView("workspaces");
  refreshWorkspaces().catch(() => {});
}

window.addEventListener("DOMContentLoaded", init);

