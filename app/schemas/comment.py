
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

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
