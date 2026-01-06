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

    def _volume_name(self, workspace_id: str) -> str:
        return f"{self.prefix}{workspace_id}-data"

    def _get(self, workspace_id: str):
        return self.client.containers.get(self._container_name(workspace_id))

    def _get_published_port(self, container) -> str | None:
        try:
            ports = container.attrs["NetworkSettings"]["Ports"]
            entry = ports.get("8080/tcp")
            if not entry:
                return None
            return entry[0]["HostPort"]
        except Exception:
            return None

    def create(self, workspace_id: str, display_name: str) -> ProvisionResult:
        name = self._container_name(workspace_id)
        try:
            vol = self.client.volumes.create(name=self._volume_name(workspace_id), labels={"vde.workspace_id": workspace_id})
            # code-server 기본 포트 8080을 host random port로 publish
            c = self.client.containers.run(
                self.image,
                name=name,
                detach=True,
                environment={
                    "PASSWORD": self.password,
                },
                command=["--bind-addr", "0.0.0.0:8080", "/home/coder/project"],
                volumes={
                    vol.name: {"bind": "/home/coder/project", "mode": "rw"},
                },
                ports={"8080/tcp": None},
                labels={
                    "vde.workspace_id": workspace_id,
                    "vde.display_name": display_name,
                },
            )
            c.reload()
            port = self._get_published_port(c)
            url = f"{self.public_base_url}:{port}" if port else None
            return ProvisionResult(status="running", url=url)
        except Exception as e:
            return ProvisionResult(status="error", error=str(e))

    def start(self, workspace_id: str) -> ProvisionResult:
        try:
            c = self._get(workspace_id)
            c.start()
            c.reload()
            port = self._get_published_port(c)
            url = f"{self.public_base_url}:{port}" if port else None
            return ProvisionResult(status="running", url=url)
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
            # data volume cleanup (best effort)
            try:
                v = self.client.volumes.get(self._volume_name(workspace_id))
                v.remove(force=True)
            except Exception:
                pass
            return ProvisionResult(status="deleted")
        except NotFound:
            # container not found, still try volume cleanup
            try:
                v = self.client.volumes.get(self._volume_name(workspace_id))
                v.remove(force=True)
            except Exception:
                pass
            return ProvisionResult(status="deleted")
        except Exception as e:
            return ProvisionResult(status="error", error=str(e))

