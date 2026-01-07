from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Admin auth (MVP)
    # - 운영에서는 SSO/프록시 기반으로 대체 권장
    admin_api_key: str = Field(default="dev-admin-key", alias="ADMIN_API_KEY")

    # Gateway (for AI proxy calls)
    gateway_base_url: str = Field(default="http://gateway:8081", alias="GATEWAY_BASE_URL")

    # IdP (for SSO/JWT mock)
    idp_base_url: str = Field(default="http://idp:8080", alias="IDP_BASE_URL")

    # Workspace provisioner
    # - mock: 상태만 관리(테스트/로컬)
    # - docker: Docker Engine으로 code-server 컨테이너 생성/중지/삭제
    workspace_provisioner: str = Field(default="mock", alias="WORKSPACE_PROVISIONER")

    # Workspace image (for docker provisioner)
    workspace_image: str = Field(default="codercom/code-server:4.95.3", alias="WORKSPACE_IMAGE")
    workspace_container_prefix: str = Field(default="vde-ws-", alias="WORKSPACE_CONTAINER_PREFIX")

    # code-server auth (MVP)
    # - 데모에서는 password 방식, 운영에서는 SSO 프록시 전제
    workspace_code_server_password: str = Field(default="dev-only", alias="WORKSPACE_PASSWORD")

    # Public base URL for generated workspace links (admin UI)
    # 예: http://localhost  (host에서 포트 매핑으로 접근하는 데모 기준)
    workspace_public_base_url: str = Field(default="http://localhost", alias="WORKSPACE_PUBLIC_BASE_URL")


settings = Settings()

