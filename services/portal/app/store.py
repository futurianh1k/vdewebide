import time
import uuid
from typing import Dict, Optional, List

from .models import WorkspaceResponse


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

