from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from app.core import messages
from app.core.constants import (
    EMAIL_MAX_LENGTH,
    FULL_NAME_MAX_LENGTH,
    FULL_NAME_MIN_LENGTH,
    PASSWORD_MIN_LENGTH,
)
from app.core.enums import UserRole


class UserBase(BaseModel):
    email: EmailStr = Field(max_length=EMAIL_MAX_LENGTH)

    full_name: str = Field(
        min_length=FULL_NAME_MIN_LENGTH,
        max_length=FULL_NAME_MAX_LENGTH,
    )

    @field_validator("full_name", mode="before")
    @classmethod
    def strip_full_name(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value


class UserCreate(UserBase):
    password: str = Field(min_length=PASSWORD_MIN_LENGTH)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    full_name: str | None = Field(
        default=None,
        min_length=FULL_NAME_MIN_LENGTH,
        max_length=FULL_NAME_MAX_LENGTH,
    )

    @model_validator(mode="before")
    @classmethod
    def validate_update(cls, data):
        if (
            isinstance(data, dict)
            and "full_name" in data
            and data.get("full_name", ...) is None
        ):
            raise ValueError(messages.FULL_NAME_CANNOT_BE_NULL)

        return data


class UserAdminUpdate(BaseModel):
    role: UserRole | None = None
    is_active: bool | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_null(cls, data):
        if isinstance(data, dict):
            for field in ("role", "is_active"):
                if field in data and data[field] is None:
                    raise ValueError(messages.FIELD_CANNOT_BE_NULL.format(field=field))

        return data


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(min_length=PASSWORD_MIN_LENGTH)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    role: UserRole
    is_active: bool
    created_at: datetime
