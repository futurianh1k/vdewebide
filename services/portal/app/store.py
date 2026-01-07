import time
import uuid
from typing import Dict, Optional, List

from .models import WorkspaceResponse, TenantResponse, ProjectResponse, UserResponse


class WorkspaceStore:
    """
    MVP용 간단 스토어(in-memory).
    운영에서는 DB(예: Postgres) + 감사/권한 모델로 확장한다.
    """

    def __init__(self):
        self._workspaces: Dict[str, WorkspaceResponse] = {}

    def list(self) -> List[WorkspaceResponse]:
        return list(self._workspaces.values())

    def get(self, wid: str) -> Optional[WorkspaceResponse]:
        return self._workspaces.get(wid)

    def create(self, name: str, owner_user_id: str, project_id: str, provider: str) -> WorkspaceResponse:
        wid = "ws-" + uuid.uuid4().hex[:10]
        ws = WorkspaceResponse(
            id=wid,
            name=name,
            owner_user_id=owner_user_id,
            project_id=project_id,
            status="created",
            created_at_ms=int(time.time() * 1000),
            url=None,
            provider=provider,
        )
        self._workspaces[wid] = ws
        return ws

    def update(self, wid: str, **kwargs) -> WorkspaceResponse:
        ws = self._workspaces[wid]
        ws = ws.model_copy(update=kwargs)
        self._workspaces[wid] = ws
        return ws

    def delete(self, wid: str):
        if wid in self._workspaces:
            del self._workspaces[wid]


class TenantStore:
    """
    SaaS white-label mock: tenant/project/user lifecycle.
    운영에서는 DB + RBAC + 감사/프로비저닝으로 확장한다.
    """
    def __init__(self):
        self._tenants: Dict[str, TenantResponse] = {}

    def list(self) -> List[TenantResponse]:
        return list(self._tenants.values())

    def get(self, tenant_id: str) -> Optional[TenantResponse]:
        return self._tenants.get(tenant_id)

    def create(self, name: str) -> TenantResponse:
        tid = "t-" + uuid.uuid4().hex[:10]
        t = TenantResponse(id=tid, name=name, created_at_ms=int(time.time() * 1000))
        self._tenants[tid] = t
        return t


class ProjectStore:
    def __init__(self):
        self._projects: Dict[str, ProjectResponse] = {}

    def list(self, tenant_id: Optional[str] = None) -> List[ProjectResponse]:
        items = list(self._projects.values())
        if tenant_id:
            items = [p for p in items if p.tenant_id == tenant_id]
        return items

    def get(self, project_id: str) -> Optional[ProjectResponse]:
        return self._projects.get(project_id)

    def create(self, tenant_id: str, name: str) -> ProjectResponse:
        pid = "p-" + uuid.uuid4().hex[:10]
        p = ProjectResponse(id=pid, tenant_id=tenant_id, name=name, created_at_ms=int(time.time() * 1000))
        self._projects[pid] = p
        return p


class UserStore:
    def __init__(self):
        self._users: Dict[str, UserResponse] = {}

    def list(self, tenant_id: Optional[str] = None) -> List[UserResponse]:
        items = list(self._users.values())
        if tenant_id:
            items = [u for u in items if u.tenant_id == tenant_id]
        return items

    def get(self, tenant_id: str, user_id: str) -> Optional[UserResponse]:
        return self._users.get(f"{tenant_id}:{user_id}")

    def create(self, tenant_id: str, user_id: str, display_name: str, role: str) -> UserResponse:
        key = f"{tenant_id}:{user_id}"
        u = UserResponse(
            tenant_id=tenant_id,
            user_id=user_id,
            display_name=display_name,
            role=role,
            created_at_ms=int(time.time() * 1000),
        )
        self._users[key] = u
        return u

