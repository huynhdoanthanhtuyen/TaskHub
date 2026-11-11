import hashlib
from uuid import UUID

import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.core.enums import TokenType
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

        if user is None:
            raise InvalidCredentialsError()

        is_valid = await run_in_threadpool(
            verify_password,
            credentials.password,
            user.hashed_password,
        )

        if not is_valid:
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InactiveUserError()

        try:
            tokens = await self._create_token_pair(user.id)
            await self.session.commit()
            return tokens

        except Exception:
            await self.session.rollback()
            raise

    async def refresh(self, request: RefreshTokenRequest) -> TokenResponse:
        try:
            payload = decode_token(request.refresh_token, TokenType.REFRESH)
        except jwt.InvalidTokenError as exc:
            raise InvalidTokenError() from exc

        user_id = payload.sub
        jti_hash = hashlib.sha256(str(payload.jti).encode("utf-8")).hexdigest()

        try:
            old_token = await self.refresh_token_repository.revoke_if_active(jti_hash)

            if old_token is None:
                raise InvalidTokenError()

            user = await self.user_repository.get_by_id(user_id)

            if user is None:
                raise InvalidTokenError()

            if not user.is_active:
                raise InactiveUserError()

            tokens = await self._create_token_pair(user.id)

            await self.session.commit()
            return tokens

        except Exception:
            await self.session.rollback()
            raise

    async def logout(self, request: RefreshTokenRequest) -> None:
        try:
            payload = decode_token(request.refresh_token, TokenType.REFRESH)
        except jwt.InvalidTokenError as exc:
            raise InvalidTokenError() from exc
        jti_hash = hashlib.sha256(str(payload.jti).encode("utf-8")).hexdigest()
        try:
            revoked_token = await self.refresh_token_repository.revoke_if_active(
                jti_hash
            )
            if revoked_token is None:
                raise InvalidTokenError()

            if revoked_token.user_id != payload.sub:
                raise InvalidTokenError()
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

    async def _create_token_pair(self, user_id: UUID) -> TokenResponse:
        access_token = create_token(user_id, TokenType.ACCESS)
        refresh_token = create_token(user_id, TokenType.REFRESH)

        refresh_payload = decode_token(refresh_token, TokenType.REFRESH)

        jti_hash = hashlib.sha256(str(refresh_payload.jti).encode("utf-8")).hexdigest()

        token_record = RefreshToken(
            user_id=user_id,
            jti_hash=jti_hash,
            expires_at=refresh_payload.exp,
        )

        await self.refresh_token_repository.create(token_record)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
