
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import COMMENT_MAX_LENGTH


class CommentBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class CommentCreate(CommentBase):
    content: str = Field(
        min_length=1,
        max_length=COMMENT_MAX_LENGTH,
    )


class CommentUpdate(CommentBase):
    content: str = Field(
        min_length=1,
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
