from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import jwt
from jwt import InvalidTokenError as JWTInvalidTokenError
from pydantic import ValidationError

from app.core.config import settings
from app.core.enums import TokenType
from app.core.exceptions import InvalidTokenError
from app.schemas.token import TokenPayload


def create_token(
    user_id: UUID,
    token_type: TokenType,
) -> str:
    now = datetime.now(UTC)

    if token_type == TokenType.ACCESS:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    elif token_type == TokenType.REFRESH:
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    else:
        raise ValueError("Unsupported token type")

    payload = {
        "sub": str(user_id),
        "type": token_type.value,
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
) -> TokenPayload:
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

        token_payload = TokenPayload.model_validate(payload)

        if token_payload.type != expected_type:
            raise InvalidTokenError()

        return token_payload

    except (JWTInvalidTokenError, ValidationError, ValueError) as exc:
        raise InvalidTokenError() from exc
