import hashlib
from datetime import UTC, datetime
from uuid import UUID

import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from app.core.jwt import create_token, decode_token
from app.core.security import verify_password
from app.models.refresh_token import RefreshToken
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.token import RefreshTokenRequest, TokenResponse
from app.schemas.user import UserLogin


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
    ):
        self.session = session
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository

    async def login(self, credentials: UserLogin) -> TokenResponse:
        email = str(credentials.email).strip().lower()

        user = await self.user_repository.get_by_email(email)

        if user is None or not verify_password(
            credentials.password,
            user.hashed_password,
        ):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InactiveUserError()

        access_token = create_token(user.id, "access")
        refresh_token = create_token(user.id, "refresh")

        refresh_payload = decode_token(refresh_token, "refresh")

        jti = refresh_payload["jti"]
        expires_at = datetime.fromtimestamp(
            refresh_payload["exp"],
            tz=UTC,
        )

        jti_hash = hashlib.sha256(jti.encode("utf-8")).hexdigest()

        token_record = RefreshToken(
            user_id=user.id,
            jti_hash=jti_hash,
            expires_at=expires_at,
        )

        try:
            await self.refresh_token_repository.create(token_record)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def refresh(self, request: RefreshTokenRequest) -> TokenResponse:
        try:
            payload = decode_token(request.refresh_token, "refresh")
        except jwt.InvalidTokenError as exc:
            raise InvalidTokenError() from exc

        user_id = UUID(payload["sub"])
        jti_hash = hashlib.sha256(payload["jti"].encode("utf-8")).hexdigest()

        try:
            old_token = await self.refresh_token_repository.revoke_if_active(jti_hash)
            if old_token is None:
                raise InvalidTokenError()
            user = await self.user_repository.get_by_id(user_id)
            if user is None:
                raise InvalidTokenError()
            if not user.is_active:
                raise InactiveUserError()

            access_token = create_token(user.id, "access")
            refresh_token = create_token(user.id, "refresh")

            refresh_payload = decode_token(
                refresh_token,
                "refresh",
            )

            new_jti_hash = hashlib.sha256(
                refresh_payload["jti"].encode("utf-8")
            ).hexdigest()

            expires_at = datetime.fromtimestamp(
                refresh_payload["exp"],
                tz=UTC,
            )

            new_token_record = RefreshToken(
                user_id=user.id,
                jti_hash=new_jti_hash,
                expires_at=expires_at,
            )

            await self.refresh_token_repository.create(new_token_record)
            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def logout(self, request: RefreshTokenRequest) -> None:
        try:
            payload = decode_token(request.refresh_token, "refresh")
        except jwt.InvalidTokenError as exc:
            raise InvalidTokenError() from exc
        jti_hash = hashlib.sha256(payload["jti"].encode("utf-8")).hexdigest()
        try:
            revoked_token = await self.refresh_token_repository.revoke_if_active(
                jti_hash
            )
            if revoked_token is None:
                raise InvalidTokenError()

            if revoked_token.user_id != UUID(payload["sub"]):
                raise InvalidTokenError()
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
