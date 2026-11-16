from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.repository import RepositoryRead


class WorkflowRunCreate(BaseModel):
    repository_id: int = Field(gt=0)
    github_id: str = Field(min_length=1, max_length=80)
    workflow_name: str = Field(min_length=1, max_length=255)
    branch: str = Field(min_length=1, max_length=255)
    commit_sha: str | None = Field(default=None, max_length=64)
    status: str = Field(min_length=1, max_length=40)
    conclusion: str | None = Field(default=None, max_length=40)
    started_at: datetime
    duration_seconds: int = Field(default=0, ge=0)
    html_url: str | None = Field(default=None, max_length=500)


class WorkflowRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    repository_id: int
    github_id: str
    workflow_name: str
    branch: str
    commit_sha: str | None
    status: str
    conclusion: str | None
    started_at: datetime
    duration_seconds: int
    html_url: str | None
    repository: RepositoryRead


class WorkflowRunPage(BaseModel):
    items: list[WorkflowRunRead]
    total: int
    page: int
    page_size: int

class WorkflowRunUpdate(BaseModel):
    status: str | None = Field(default=None, min_length=1, max_length=40)
    conclusion: str | None = Field(default=None, max_length=40)
    duration_seconds: int | None = Field(default=None, ge=0)
    html_url: str | None = Field(default=None, max_length=500)