from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .config import settings
from .auth import AdminAuthMiddleware
from .store import WorkspaceStore
from .models import WorkspaceCreateRequest
from .provisioners.mock import MockProvisioner
from .provisioners.docker_provider import DockerProvisioner


app = FastAPI(title="Admin Portal", version="0.1.0")
app.add_middleware(AdminAuthMiddleware)

store = WorkspaceStore()
STATIC_DIR = (Path(__file__).resolve().parents[1] / "static").resolve()


def _get_provisioner():
    if settings.workspace_provisioner == "docker":
        return DockerProvisioner(
            image=settings.workspace_image,
            prefix=settings.workspace_container_prefix,
            password=settings.workspace_code_server_password,
            public_base_url=settings.workspace_public_base_url,
        )
    return MockProvisioner(public_base_url=settings.workspace_public_base_url)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def root():
    return HTMLResponse('<meta http-equiv="refresh" content="0; url=/admin">')


@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    html_path = STATIC_DIR / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/api/workspaces")
def list_workspaces():
    return {"items": [w.model_dump() for w in store.list()]}


@app.post("/api/workspaces")
def create_workspace(req: WorkspaceCreateRequest):
    prov = _get_provisioner()
    ws = store.create(req.name, req.owner_user_id, req.project_id, provider=prov.name)
    res = prov.create(ws.id, ws.name)
    ws = store.update(ws.id, status=res.status, url=res.url)
    return ws.model_dump()


@app.post("/api/workspaces/{workspace_id}/start")
def start_workspace(workspace_id: str):
    ws = store.get(workspace_id)
    if not ws:
        return {"error": {"code": "NOT_FOUND"}}
    prov = _get_provisioner()
    res = prov.start(workspace_id)
    ws = store.update(workspace_id, status=res.status, url=res.url or ws.url)
    return ws.model_dump()


@app.post("/api/workspaces/{workspace_id}/stop")
def stop_workspace(workspace_id: str):
    ws = store.get(workspace_id)
    if not ws:
        return {"error": {"code": "NOT_FOUND"}}
    prov = _get_provisioner()
    res = prov.stop(workspace_id)
    ws = store.update(workspace_id, status=res.status)
    return ws.model_dump()


@app.delete("/api/workspaces/{workspace_id}")
def delete_workspace(workspace_id: str):
    ws = store.get(workspace_id)
    if not ws:
        return {"ok": True}
    prov = _get_provisioner()
    prov.delete(workspace_id)
    store.delete(workspace_id)
    return {"ok": True}


@app.post("/api/gateway/{path:path}")
async def proxy_gateway(path: str, request: Request):
    """
    Admin UI에서 Gateway 호출을 테스트하기 위한 프록시 엔드포인트.
    - 운영에서는 별도 접근통제(tenant/project scope)와 감사 로깅이 필요.
    """
    import httpx

    url = f"{settings.gateway_base_url}/{path}"
    body = await request.body()
    headers = dict(request.headers)
    # admin key 등 내부 헤더 제거
    headers.pop("x-admin-key", None)

    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.request(request.method, url, content=body, headers=headers)
        return (r.json() if "application/json" in r.headers.get("content-type", "") else {"raw": r.text})

