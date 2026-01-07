from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    # Upstreams
    upstream_tabby: str = Field(default="http://tabby:8080", alias="UPSTREAM_TABBY")
    upstream_agent: str = Field(default="http://opencode-model:8080", alias="UPSTREAM_AGENT")
    upstream_chat: str  = Field(default="http://chat-llm:8080", alias="UPSTREAM_CHAT")
    upstream_rag: str   = Field(default="http://code-rag:8080", alias="UPSTREAM_RAG")

    # JWT / Auth
    jwt_dev_mode: bool = Field(default=False, alias="JWT_DEV_MODE")
    jwt_jwks_url: Optional[str] = Field(default=None, alias="JWT_JWKS_URL")
    jwt_jwks_file: Optional[str] = Field(default=None, alias="JWT_JWKS_FILE")
    jwt_audience: Optional[str] = Field(default=None, alias="JWT_AUDIENCE")
    jwt_issuer: Optional[str] = Field(default=None, alias="JWT_ISSUER")

    # JWKS cache/refresh
    jwt_jwks_cache_ttl_seconds: int = Field(default=300, alias="JWT_JWKS_CACHE_TTL_SECONDS")
    jwt_jwks_refresh_seconds: int = Field(default=60, alias="JWT_JWKS_REFRESH_SECONDS")
    jwt_jwks_fail_open: bool = Field(default=False, alias="JWT_JWKS_FAIL_OPEN")  # false => fail close

    # DLP
    # 기본값은 gateway 패키지 루트 기준으로 고정하여, 실행 위치(cwd)에 영향을 받지 않도록 한다.
    dlp_rules_path: str = Field(
        default=str((Path(__file__).resolve().parents[1] / "policies" / "dlp_rules.yaml")),
        alias="DLP_RULES_PATH",
    )
    dlp_reload_seconds: int = Field(default=30, alias="DLP_RELOAD_SECONDS")
    dlp_stream_mode: str = Field(default="pre_only", alias="DLP_STREAM_MODE")  # pre_only | pre_and_incremental
    dlp_stream_max_buffer_bytes: int = Field(default=1048576, alias="DLP_STREAM_MAX_BUFFER_BYTES")

    # Audit DB
    audit_db_dsn: Optional[str] = Field(default=None, alias="AUDIT_DB_DSN")
    audit_retention_days: int = Field(default=365, alias="AUDIT_RETENTION_DAYS")

    # Upstream auth separation
    upstream_auth_mode: str = Field(default="none", alias="UPSTREAM_AUTH_MODE")  # none|static_bearer|mtls
    upstream_bearer_token: Optional[str] = Field(default=None, alias="UPSTREAM_BEARER_TOKEN")
    upstream_ca_file: Optional[str] = Field(default=None, alias="UPSTREAM_CA_FILE")
    upstream_client_cert_file: Optional[str] = Field(default=None, alias="UPSTREAM_CLIENT_CERT_FILE")
    upstream_client_key_file: Optional[str] = Field(default=None, alias="UPSTREAM_CLIENT_KEY_FILE")

    # HTTP
    upstream_timeout_seconds: float = Field(default=30.0, alias="UPSTREAM_TIMEOUT_SECONDS")
    stream_read_timeout_seconds: float = Field(default=60.0, alias="STREAM_READ_TIMEOUT_SECONDS")

    # Ops (MVP)
    # - 운영에서는 mTLS/mesh/RBAC 등으로 보호하고, 애플리케이션 레벨 키는 보조 수단으로만 사용 권장
    ops_retention_purge_key: Optional[str] = Field(default=None, alias="OPS_RETENTION_PURGE_KEY")
    ops_policy_key: Optional[str] = Field(default=None, alias="OPS_POLICY_KEY")

settings = Settings()
