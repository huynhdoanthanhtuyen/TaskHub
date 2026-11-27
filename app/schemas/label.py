from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core import messages
from app.core.constants import (
    LABEL_COLOR_MAX_LENGTH,
    LABEL_COLOR_PATTERN,
    LABEL_NAME_MAX_LENGTH,
    LABEL_NAME_MIN_LENGTH,
)
from app.schemas.base import BaseSchema


class LabelCreate(BaseSchema):
    name: str = Field(
        min_length=LABEL_NAME_MIN_LENGTH,
        max_length=LABEL_NAME_MAX_LENGTH,
    )
    color: str = Field(
        max_length=LABEL_COLOR_MAX_LENGTH,
        pattern=LABEL_COLOR_PATTERN,
    )


class LabelUpdate(BaseSchema):
    name: str | None = Field(
        default=None,
        min_length=LABEL_NAME_MIN_LENGTH,
        max_length=LABEL_NAME_MAX_LENGTH,
    )
    color: str | None = Field(
        default=None,
        max_length=LABEL_COLOR_MAX_LENGTH,
        pattern=LABEL_COLOR_PATTERN,
    )

    @model_validator(mode="after")
    def validate_non_nullable_fields(self):
        for field in ("name", "color"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(messages.FIELD_CANNOT_BE_NULL.format(field=field))
        return self


class LabelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    name: str
    color: str


class LabelListResponse(BaseModel):
    items: list[LabelResponse]
    total: int
    offset: int
    limit: int
