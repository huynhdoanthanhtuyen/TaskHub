from datetime import UTC, datetime
from uuid import UUID

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.core import messages
from app.core.constants import (
    DESCRIPTION_MAX_LENGTH,
    TITLE_MAX_LENGTH,
    TITLE_MIN_LENGTH,
)
from app.core.enums import TaskPriority, TaskStatus


class TaskBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class TaskCreate(TaskBase):
    title: str = Field(
        min_length=TITLE_MIN_LENGTH,
        max_length=TITLE_MAX_LENGTH,
    )
    description: str | None = Field(
        default=None,
        max_length=DESCRIPTION_MAX_LENGTH,
    )
    assignee_id: UUID | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: AwareDatetime | None = None

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, value: datetime | None):
        if value is not None and value <= datetime.now(UTC):
            raise ValueError(messages.TASK_DUE_DATE_MUST_BE_IN_FUTURE)
        return value


class TaskUpdate(TaskBase):
    title: str | None = Field(
        default=None,
        min_length=TITLE_MIN_LENGTH,
        max_length=TITLE_MAX_LENGTH,
    )
    description: str | None = Field(
        default=None,
        max_length=DESCRIPTION_MAX_LENGTH,
    )
    assignee_id: UUID | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: AwareDatetime | None = None

    @model_validator(mode="after")
    def validate_non_nullable_fields(self):
        for field in ("title", "status", "priority"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(messages.FIELD_CANNOT_BE_NULL.format(field=field))
        return self

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, value: datetime | None):
        if value is not None and value <= datetime.now(UTC):
            raise ValueError(messages.TASK_DUE_DATE_MUST_BE_IN_FUTURE)
        return value


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    assignee_id: UUID | None
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    due_date: datetime | None
    created_by: UUID
    created_at: datetime


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    offset: int
    limit: int
