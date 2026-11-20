import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.constants import (
    PROJECT_DESCRIPTION_MAX_LENGTH,
    PROJECT_NAME_MAX_LENGTH,
)
from app.core.enums import ProjectStatus


class ProjectCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=PROJECT_NAME_MAX_LENGTH,
    )
    description: str | None = Field(
        default=None,
        max_length=PROJECT_DESCRIPTION_MAX_LENGTH,
    )


class ProjectUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=PROJECT_NAME_MAX_LENGTH,
    )
    description: str | None = Field(
        default=None,
        max_length=PROJECT_DESCRIPTION_MAX_LENGTH,
    )
    status: ProjectStatus | None = None

    @model_validator(mode="after")
    def validate_non_nullable_fields(self):
        for field in ("name", "status"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    description: str | None
    status: ProjectStatus
    created_at: datetime


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    total: int
    offset: int
    limit: int
