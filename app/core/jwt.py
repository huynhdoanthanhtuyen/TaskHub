from datetime import UTC, datetime, timedelta
from typing import Any, Literal
from uuid import UUID, uuid4

import jwt
from jwt import InvalidTokenError

from app.core.config import settings

TokenType = Literal["access", "refresh"]


def create_token(
    user_id: UUID,
    token_type: TokenType,
) -> str:
    now = datetime.now(UTC)

    if token_type == "access":
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": str(user_id),
        "type": token_type,
        "jti": str(uuid4()),
        "iat": now,
        "exp": now + expires_delta,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_token(
    token: str,
    expected_type: TokenType,
) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "require": [
                    "sub",
                    "type",
                    "jti",
                    "iat",
                    "exp",
                ]
            },
        )

        if payload.get("type") != expected_type:
            raise InvalidTokenError("Invalid token type")

        UUID(payload["sub"])
        UUID(payload["jti"])

        return payload

    except (InvalidTokenError, ValueError, KeyError) as exc:
        raise InvalidTokenError("Invalid or expired token") from exc
