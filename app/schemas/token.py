from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from app.core.enums import TokenType


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenPayload(BaseModel):
    sub: UUID
    type: TokenType
    jti: UUID
    iat: datetime
    exp: datetime
