from pydantic import BaseModel, Field
from typing import Optional, Literal


WorkspaceStatus = Literal["created", "running", "stopped", "deleted", "error"]

class TenantCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)


class TenantResponse(BaseModel):
    id: str
    name: str
    created_at_ms: int


class ProjectCreateRequest(BaseModel):
    tenant_id: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=80)


class ProjectResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    created_at_ms: int


class UserCreateRequest(BaseModel):
    tenant_id: str = Field(min_length=1, max_length=80)
    user_id: str = Field(min_length=1, max_length=80)
    display_name: str = Field(default="Developer", min_length=1, max_length=80)
    role: str = Field(default="developer", min_length=1, max_length=40)


class UserResponse(BaseModel):
    tenant_id: str
    user_id: str
    display_name: str
    role: str
    created_at_ms: int


class PocBootstrapRequest(BaseModel):
    tenant_name: str = Field(default="Demo Tenant", min_length=1, max_length=80)
    project_name: str = Field(default="Demo Project", min_length=1, max_length=80)
    user_id: str = Field(default="demo-user", min_length=1, max_length=80)
    user_display_name: str = Field(default="Demo User", min_length=1, max_length=80)
    user_role: str = Field(default="admin", min_length=1, max_length=40)
    workspace_name: str = Field(default="demo-workspace", min_length=1, max_length=80)


class WorkspaceCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    owner_user_id: str = Field(default="dev-user", min_length=1, max_length=80)
    project_id: str = Field(default="dev-project", min_length=1, max_length=80)


class WorkspaceResponse(BaseModel):
    id: str
    name: str
    owner_user_id: str
    project_id: str
    status: WorkspaceStatus
    created_at_ms: int
    url: Optional[str] = None
    provider: str

