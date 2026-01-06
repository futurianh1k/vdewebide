from typing import Optional

import docker
from docker.errors import NotFound

from .base import WorkspaceProvisioner, ProvisionResult


class DockerProvisioner(WorkspaceProvisioner):
    name = "docker"

    def __init__(self, image: str, prefix: str, password: str, public_base_url: str):
        self.image = image
        self.prefix = prefix
        self.password = password
        self.public_base_url = public_base_url.rstrip("/")
        self.client = docker.from_env()

    def _container_name(self, workspace_id: str) -> str:
        return f"{self.prefix}{workspace_id}"

    def _get(self, workspace_id: str):
        return self.client.containers.get(self._container_name(workspace_id))

    def create(self, workspace_id: str, display_name: str) -> ProvisionResult:
        name = self._container_name(workspace_id)
        try:
            # code-server 기본 포트 8080을 host random port로 publish
            c = self.client.containers.run(
                self.image,
                name=name,
                detach=True,
                environment={
                    "PASSWORD": self.password,
                },
                ports={"8080/tcp": None},
                labels={
                    "vde.workspace_id": workspace_id,
                    "vde.display_name": display_name,
                },
            )
            c.reload()
            port = c.attrs["NetworkSettings"]["Ports"]["8080/tcp"][0]["HostPort"]
            return ProvisionResult(status="running", url=f"{self.public_base_url}:{port}")
        except Exception as e:
            return ProvisionResult(status="error", error=str(e))

    def start(self, workspace_id: str) -> ProvisionResult:
        try:
            c = self._get(workspace_id)
            c.start()
            c.reload()
            port = c.attrs["NetworkSettings"]["Ports"]["8080/tcp"][0]["HostPort"]
            return ProvisionResult(status="running", url=f"{self.public_base_url}:{port}")
        except Exception as e:
            return ProvisionResult(status="error", error=str(e))

    def stop(self, workspace_id: str) -> ProvisionResult:
        try:
            c = self._get(workspace_id)
            c.stop(timeout=5)
            return ProvisionResult(status="stopped")
        except NotFound:
            return ProvisionResult(status="error", error="not_found")
        except Exception as e:
            return ProvisionResult(status="error", error=str(e))

    def delete(self, workspace_id: str) -> ProvisionResult:
        try:
            c = self._get(workspace_id)
            c.remove(force=True)
            return ProvisionResult(status="deleted")
        except NotFound:
            return ProvisionResult(status="deleted")
        except Exception as e:
            return ProvisionResult(status="error", error=str(e))

