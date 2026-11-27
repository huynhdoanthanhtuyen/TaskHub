import uuid
from datetime import datetime

from pydantic import ConfigDict, Field, model_validator

from app.core.constants import (
    PROJECT_DESCRIPTION_MAX_LENGTH,
    PROJECT_NAME_MAX_LENGTH,
    PROJECT_NAME_MIN_LENGTH,
)
from app.core.enums import ProjectStatus
from app.core.messages import FIELD_CANNOT_BE_NULL
from app.schemas.base import BaseSchema


class ProjectCreate(BaseSchema):
    name: str = Field(
        min_length=PROJECT_NAME_MIN_LENGTH,
        max_length=PROJECT_NAME_MAX_LENGTH,
    )
    description: str | None = Field(
        default=None,
        max_length=PROJECT_DESCRIPTION_MAX_LENGTH,
    )


class ProjectUpdate(BaseSchema):
    name: str | None = Field(
        default=None,
        min_length=PROJECT_NAME_MIN_LENGTH,
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
                raise ValueError(FIELD_CANNOT_BE_NULL.format(field=field))
        return self


class ProjectResponse(BaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    description: str | None
    status: ProjectStatus
    created_at: datetime


class ProjectListResponse(BaseSchema):
    items: list[ProjectResponse]
    total: int
    offset: int
    limit: int
