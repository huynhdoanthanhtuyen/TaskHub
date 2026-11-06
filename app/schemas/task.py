from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.constants import (
    DESCRIPTION_MAX_LENGTH,
    TITLE_MAX_LENGTH,
    TITLE_MIN_LENGTH,
)


class TaskBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class TaskCreate(TaskBase):
    title: str = Field(
        min_length=TITLE_MIN_LENGTH,
        max_length=TITLE_MAX_LENGTH,
        description="Title of task",
    )
    description: str | None = Field(default=None, max_length=DESCRIPTION_MAX_LENGTH)


class TaskUpdate(TaskBase):
    title: str | None = Field(
        default=None, min_length=TITLE_MIN_LENGTH, max_length=TITLE_MAX_LENGTH
    )
    description: str | None = Field(default=None, max_length=DESCRIPTION_MAX_LENGTH)
    completed: bool | None = None

    @field_validator("title", "completed")
    @classmethod
    def prevent_null(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value


class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    completed: bool
