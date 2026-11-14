from datetime import UTC, datetime
from uuid import UUID

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from app.core.constants import (
    DESCRIPTION_MAX_LENGTH,
    TITLE_MAX_LENGTH,
    TITLE_MIN_LENGTH,
)
from app.core.enums import TaskPriority, TaskStatus


class TaskBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class TaskCreate(TaskBase):
    project_id: UUID

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
                raise ValueError("Due date must be in the future")
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

    @field_validator("title", "status", "priority")
    @classmethod
    def prevent_null(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, value: datetime | None):
        if value is not None and value <= datetime.now(UTC):
            raise ValueError("Due date must be in the future")
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
    skip: int
    limit: int
