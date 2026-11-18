import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import WORKSPACE_NAME_MAX_LENGTH, WORKSPACE_NAME_MIN_LENGTH
from app.core.enums import WorkspaceRole


class WorkspaceBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class WorkspaceCreate(WorkspaceBase):
    name: str = Field(
        min_length=WORKSPACE_NAME_MIN_LENGTH, max_length=WORKSPACE_NAME_MAX_LENGTH
    )


class WorkspaceUpdate(WorkspaceBase):
    name: str = Field(
        min_length=WORKSPACE_NAME_MIN_LENGTH, max_length=WORKSPACE_NAME_MAX_LENGTH
    )


class WorkspaceResponse(WorkspaceBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    owner_id: uuid.UUID
    created_at: datetime


class WorkspaceMemberCreate(WorkspaceBase):
    user_id: uuid.UUID
    role: WorkspaceRole = WorkspaceRole.VIEWER


class WorkspaceMemberResponse(WorkspaceBase):
    model_config = ConfigDict(from_attributes=True)
    workspace_id: uuid.UUID
    user_id: uuid.UUID
    role: WorkspaceRole


class WorkspaceListResponse(BaseModel):
    items: list[WorkspaceResponse]
    total: int
    offset: int
    limit: int
