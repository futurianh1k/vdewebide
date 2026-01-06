from dataclasses import dataclass
from typing import Optional


@dataclass
class ProvisionResult:
    status: str
    url: Optional[str] = None
    error: Optional[str] = None


class WorkspaceProvisioner:
    name: str = "base"

    def create(self, workspace_id: str, display_name: str) -> ProvisionResult:  # pragma: no cover
        raise NotImplementedError

    def start(self, workspace_id: str) -> ProvisionResult:  # pragma: no cover
        raise NotImplementedError

    def stop(self, workspace_id: str) -> ProvisionResult:  # pragma: no cover
        raise NotImplementedError

    def delete(self, workspace_id: str) -> ProvisionResult:  # pragma: no cover
        raise NotImplementedError

