function qs(sel) { return document.querySelector(sel); }

const state = {
  view: "workspaces",
  adminKey: "",
};

function setView(name) {
  state.view = name;
  document.querySelectorAll(".nav-item").forEach((b) => b.classList.toggle("active", b.dataset.view === name));
  qs("#view-workspaces").classList.toggle("hidden", name !== "workspaces");
  qs("#view-org").classList.toggle("hidden", name !== "org");
  qs("#view-sso").classList.toggle("hidden", name !== "sso");
  qs("#view-policy").classList.toggle("hidden", name !== "policy");
  qs("#view-gateway").classList.toggle("hidden", name !== "gateway");
  qs("#pageTitle").textContent =
    name === "workspaces" ? "Workspaces" :
    name === "org" ? "Org" :
    name === "sso" ? "SSO/JWT" :
    name === "policy" ? "Policy" :
    "Gateway Test";
  qs("#pageDesc").textContent =
    name === "workspaces" ? "code-server + opencode 컨셉의 워크스페이스를 관리합니다." :
    name === "org" ? "White-label SaaS 기본 엔터티(tenant/project/user)를 Mock으로 관리합니다." :
    name === "sso" ? "Mock IdP로 JWT를 발급하고 Gateway에 붙여 호출하는 PoC 플로우를 제공합니다." :
    name === "policy" ? "DLP 룰 및 Upstream Auth를 운영(Mock) API로 조회/변경합니다." :
    "관리자 화면에서 AI Gateway 호출을 빠르게 점검합니다(데모).";
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

async function onTenantCreate() {
  const name = qs("#tenantName").value.trim();
  if (!name) return alert("Tenant name is required");
  const t = await api("/api/tenants", { method: "POST", body: JSON.stringify({ name }) });
  qs("#tenantOut").textContent = JSON.stringify(t, null, 2);
  qs("#projectTenantId").value = t.id;
  qs("#userTenantId").value = t.id;
}

async function onProjectCreate() {
  const tenant_id = qs("#projectTenantId").value.trim();
  const name = qs("#projectName").value.trim();
  if (!tenant_id || !name) return alert("tenant_id + project name are required");
  const p = await api("/api/projects", { method: "POST", body: JSON.stringify({ tenant_id, name }) });
  qs("#projectOut").textContent = JSON.stringify(p, null, 2);
  if (p.id) qs("#wsProject").value = p.id;
}

async function onUserCreate() {
  const tenant_id = qs("#userTenantId").value.trim();
  const user_id = qs("#userId").value.trim();
  const display_name = (qs("#userDisplayName").value.trim() || "Developer");
  const role = (qs("#userRole").value.trim() || "developer");
  if (!tenant_id || !user_id) return alert("tenant_id + user_id are required");
  const u = await api("/api/users", { method: "POST", body: JSON.stringify({ tenant_id, user_id, display_name, role }) });
  qs("#userOut").textContent = JSON.stringify(u, null, 2);
  if (u.user_id) qs("#wsOwner").value = u.user_id;
}

async function onIssueToken() {
  qs("#idpOut").textContent = "loading...";
  const payload = {
    sub: qs("#idpSub").value.trim() || "dev-user",
    tid: qs("#idpTid").value.trim() || "dev-tenant",
    pid: qs("#idpPid").value.trim() || "dev-project",
    wid: qs("#idpWid").value.trim() || "dev-workspace",
    role: qs("#idpRole").value.trim() || "developer",
    iss: qs("#idpIss").value.trim() || "vde-idp",
    aud: qs("#idpAud").value.trim() || "vde-gateway",
  };
  // via portal proxy (no CORS)
  const r = await api("/api/idp/token", { method: "POST", body: JSON.stringify(payload) });
  const bearer = r.access_token ? `Bearer ${r.access_token}` : "";
  qs("#issuedBearer").value = bearer;
  qs("#gwAuth").value = bearer || qs("#gwAuth").value;
  qs("#opsAuth").value = bearer || qs("#opsAuth").value;
  qs("#idpOut").textContent = JSON.stringify(r, null, 2);
}

async function onCopyBearer() {
  const v = qs("#issuedBearer").value;
  if (!v) return;
  await navigator.clipboard.writeText(v).catch(() => {});
}

function opsHeaders() {
  const h = {};
  const auth = qs("#opsAuth").value.trim();
  const key = qs("#opsKey").value.trim();
  if (auth) h["Authorization"] = auth;
  if (key) h["X-Ops-Key"] = key;
  return h;
}

async function onDlpFetch() {
  qs("#dlpOut").textContent = "loading...";
  const data = await api("/api/gateway/ops/dlp/rules", { method: "POST", headers: opsHeaders(), body: "{}" });
  qs("#dlpYaml").value = data.raw || "";
  qs("#dlpOut").textContent = JSON.stringify(data, null, 2);
}

async function onDlpApply() {
  qs("#dlpOut").textContent = "loading...";
  const raw = qs("#dlpYaml").value;
  const data = await api("/api/gateway/ops/dlp/rules", {
    method: "POST",
    headers: Object.assign({ "Content-Type": "application/json" }, opsHeaders()),
    body: JSON.stringify({ raw }),
  });
  qs("#dlpOut").textContent = JSON.stringify(data, null, 2);
}

async function onUpFetch() {
  qs("#upOut").textContent = "loading...";
  const data = await api("/api/gateway/ops/upstream/auth", { method: "POST", headers: opsHeaders(), body: "{}" });
  qs("#upMode").value = data.upstream_auth_mode || "none";
  qs("#upOut").textContent = JSON.stringify(data, null, 2);
}

async function onUpApply() {
  qs("#upOut").textContent = "loading...";
  const upstream_auth_mode = qs("#upMode").value;
  const upstream_bearer_token = qs("#upBearer").value.trim();
  const payload = { upstream_auth_mode };
  if (upstream_auth_mode === "static_bearer") payload.upstream_bearer_token = upstream_bearer_token;
  const data = await api("/api/gateway/ops/upstream/auth", {
    method: "POST",
    headers: Object.assign({ "Content-Type": "application/json" }, opsHeaders()),
    body: JSON.stringify(payload),
  });
  qs("#upOut").textContent = JSON.stringify(data, null, 2);
}

function init() {
  document.querySelectorAll(".nav-item").forEach((b) => b.addEventListener("click", () => setView(b.dataset.view)));
  qs("#refreshBtn").addEventListener("click", () => refreshWorkspaces().catch((e) => alert(e.message)));
  qs("#createBtn").addEventListener("click", () => onCreate().catch((e) => alert(e.message)));
  qs("#wsTbody").addEventListener("click", (e) => onWsAction(e).catch((err) => alert(err.message)));
  qs("#gwSendBtn").addEventListener("click", () => onGatewaySend().catch((e) => alert(e.message)));
  qs("#adminKey").addEventListener("input", (e) => { state.adminKey = e.target.value; });
  qs("#tenantCreateBtn").addEventListener("click", () => onTenantCreate().catch((e) => alert(e.message)));
  qs("#projectCreateBtn").addEventListener("click", () => onProjectCreate().catch((e) => alert(e.message)));
  qs("#userCreateBtn").addEventListener("click", () => onUserCreate().catch((e) => alert(e.message)));
  qs("#idpIssueBtn").addEventListener("click", () => onIssueToken().catch((e) => alert(e.message)));
  qs("#copyBearerBtn").addEventListener("click", () => onCopyBearer().catch(() => {}));
  qs("#dlpFetchBtn").addEventListener("click", () => onDlpFetch().catch((e) => alert(e.message)));
  qs("#dlpApplyBtn").addEventListener("click", () => onDlpApply().catch((e) => alert(e.message)));
  qs("#upFetchBtn").addEventListener("click", () => onUpFetch().catch((e) => alert(e.message)));
  qs("#upApplyBtn").addEventListener("click", () => onUpApply().catch((e) => alert(e.message)));

  setView("workspaces");
  refreshWorkspaces().catch(() => {});
}

window.addEventListener("DOMContentLoaded", init);

