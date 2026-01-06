from pydantic import BaseModel, Field
from typing import Optional, Literal


WorkspaceStatus = Literal["created", "running", "stopped", "deleted", "error"]


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

