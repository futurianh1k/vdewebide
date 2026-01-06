import docker
import os
import json
from pathlib import Path
from docker.errors import NotFound

from .base import WorkspaceProvisioner, ProvisionResult


class DockerProvisioner(WorkspaceProvisioner):
    name = "docker"

    def __init__(self, image: str, prefix: str, password: str, public_base_url: str, gateway_base_url: str):
        self.image = image
        self.prefix = prefix
        self.password = password
        self.public_base_url = public_base_url.rstrip("/")
        self.gateway_base_url = gateway_base_url.rstrip("/")
        self.client = docker.from_env()
        self.network_name = self._detect_own_network()

    def _container_name(self, workspace_id: str) -> str:
        return f"{self.prefix}{workspace_id}"

    def _volume_name(self, workspace_id: str) -> str:
        return f"{self.prefix}{workspace_id}-data"

    def _config_volume_name(self, workspace_id: str) -> str:
        # ~/.config 전체를 볼륨으로 마운트(부모 디렉토리 생성 권한 이슈 방지)
        return f"{self.prefix}{workspace_id}-config"

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

    def _detect_own_network(self) -> str | None:
        """
        Portal 컨테이너가 docker-compose 네트워크에서 실행 중이면,
        워크스페이스 컨테이너도 동일 네트워크로 붙여 'gateway' 서비스명을 해석할 수 있도록 한다.
        """
        cid = os.environ.get("HOSTNAME")
        if not cid:
            return None
        try:
            me = self.client.containers.get(cid)
            nets = (me.attrs.get("NetworkSettings") or {}).get("Networks") or {}
            # 첫 번째 네트워크를 기본으로 사용
            for n in nets.keys():
                return n
        except Exception:
            return None
        return None

    @staticmethod
    def build_opencode_config(gateway_base_url: str) -> dict:
        """
        보안 원칙:
        - 토큰/시크릿을 설정 파일에 저장하지 않는다.
        - endpoint는 Gateway로만 지정한다(모델 선택/라우팅은 Gateway 정책으로 통제).
        """
        return {
            "version": "opencode-config-0.1",
            "gateway": {
                "base_url": gateway_base_url.rstrip("/"),
            },
            "security": {
                "store_tokens_in_config": False,
                "note": "Use secret mount or env for tokens; do not store in opencode.json",
            },
        }

    def _init_config_volume(self, volume_name: str) -> None:
        """
        ~/.config 볼륨을 초기화한다.
        - opencode 설정: ~/.config/opencode/opencode.json
        - code-server 설정 디렉토리: ~/.config/code-server (생성만)
        - 권한: coder(1000:1000)가 쓸 수 있도록 보장
        """
        payload = json.dumps(self.build_opencode_config(self.gateway_base_url), ensure_ascii=False, indent=2)
        cmd = [
            "python",
            "-c",
            (
                "import os, pathlib; base=pathlib.Path('/mnt/config'); "
                "op=base/'opencode'/'opencode.json'; "
                "op.parent.mkdir(parents=True, exist_ok=True); "
                f"op.write_text({payload!r}, encoding='utf-8'); "
                "cs=base/'code-server'; cs.mkdir(parents=True, exist_ok=True); "
                "os.chmod(op, 0o600); os.chmod(op.parent, 0o700); os.chmod(cs, 0o700); "
                # ownership to coder:coder (1000:1000)
                "uid=1000; gid=1000\n"
                "for p in [base, op.parent, cs, op]:\n"
                "    try:\n"
                "        os.chown(str(p), uid, gid)\n"
                "    except Exception:\n"
                "        pass\n"
                "print('initialized', str(op))"
            ),
        ]
        # init container (짧게 실행 후 자동 제거)
        self.client.containers.run(
            "python:3.12-slim",
            command=cmd,
            remove=True,
            volumes={volume_name: {"bind": "/mnt/config", "mode": "rw"}},
        )

    def create(self, workspace_id: str, display_name: str) -> ProvisionResult:
        name = self._container_name(workspace_id)
        try:
            vol = self.client.volumes.create(name=self._volume_name(workspace_id), labels={"vde.workspace_id": workspace_id})
            cfg_vol = self.client.volumes.create(name=self._config_volume_name(workspace_id), labels={"vde.workspace_id": workspace_id})
            self._init_config_volume(cfg_vol.name)
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
                    cfg_vol.name: {"bind": "/home/coder/.config", "mode": "rw"},
                },
                ports={"8080/tcp": None},
                labels={
                    "vde.workspace_id": workspace_id,
                    "vde.display_name": display_name,
                },
                network=self.network_name,
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
            try:
                v = self.client.volumes.get(self._config_volume_name(workspace_id))
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
            try:
                v = self.client.volumes.get(self._config_volume_name(workspace_id))
                v.remove(force=True)
            except Exception:
                pass
            return ProvisionResult(status="deleted")
        except Exception as e:
            return ProvisionResult(status="error", error=str(e))

