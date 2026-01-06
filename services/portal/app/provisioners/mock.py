from .base import WorkspaceProvisioner, ProvisionResult


class MockProvisioner(WorkspaceProvisioner):
    name = "mock"

    def __init__(self, public_base_url: str):
        self.public_base_url = public_base_url.rstrip("/")

    def create(self, workspace_id: str, display_name: str) -> ProvisionResult:
        # 실제 워크스페이스는 생성하지 않고 상태만 제공
        return ProvisionResult(status="created", url=f"{self.public_base_url}/__mock_workspace__/{workspace_id}")

    def start(self, workspace_id: str) -> ProvisionResult:
        return ProvisionResult(status="running", url=f"{self.public_base_url}/__mock_workspace__/{workspace_id}")

    def stop(self, workspace_id: str) -> ProvisionResult:
        return ProvisionResult(status="stopped")

    def delete(self, workspace_id: str) -> ProvisionResult:
        return ProvisionResult(status="deleted")

