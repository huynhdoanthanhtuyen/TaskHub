import uuid
from datetime import datetime

from pydantic import ConfigDict, Field

from app.core.constants import WORKSPACE_NAME_MAX_LENGTH, WORKSPACE_NAME_MIN_LENGTH
from app.core.enums import WorkspaceRole
from app.schemas.base import BaseSchema


class WorkspaceCreate(BaseSchema):
    name: str = Field(
        min_length=WORKSPACE_NAME_MIN_LENGTH, max_length=WORKSPACE_NAME_MAX_LENGTH
    )


class WorkspaceUpdate(BaseSchema):
    name: str = Field(
        min_length=WORKSPACE_NAME_MIN_LENGTH, max_length=WORKSPACE_NAME_MAX_LENGTH
    )


class WorkspaceResponse(BaseSchema):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    owner_id: uuid.UUID
    created_at: datetime


class WorkspaceMemberCreate(BaseSchema):
    user_id: uuid.UUID
    role: WorkspaceRole = WorkspaceRole.VIEWER


class WorkspaceMemberResponse(BaseSchema):
    model_config = ConfigDict(from_attributes=True)
    workspace_id: uuid.UUID
    user_id: uuid.UUID
    role: WorkspaceRole


class WorkspaceListResponse(BaseSchema):
    items: list[WorkspaceResponse]
    total: int
    offset: int
    limit: int
