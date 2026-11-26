from datetime import datetime
from uuid import UUID

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.core import messages
from app.core.constants import COMMENT_MAX_LENGTH, COMMENT_MIN_LENGTH
from app.schemas.base import BaseSchema


class CommentCreate(BaseSchema):
    content: str = Field(
        min_length=COMMENT_MIN_LENGTH,
        max_length=COMMENT_MAX_LENGTH,
    )


class CommentUpdate(BaseSchema):
    content: str = Field(
        min_length=COMMENT_MIN_LENGTH,
        max_length=COMMENT_MAX_LENGTH,
    )


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    task_id: UUID
    author_id: UUID
    content: str
    created_at: datetime


class CommentListResponse(BaseModel):
    items: list[CommentResponse]
    total: int
    offset: int
    limit: int


class CommentFilter(BaseModel):
    author_id: UUID | None = None
    created_from: AwareDatetime | None = None
    created_to: AwareDatetime | None = None

    @model_validator(mode="after")
    def validate_date_range(self):
        if (
            self.created_from is not None
            and self.created_to is not None
            and self.created_from > self.created_to
        ):
            raise ValueError(messages.INVALID_DATE_RANGE)

        return self
