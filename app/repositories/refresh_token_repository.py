from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: AsyncSession):
        super().__init__(RefreshToken, session)

    async def get_by_jti_hash(
        self,
        jti_hash: str,
    ) -> RefreshToken | None:
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.jti_hash == jti_hash)
        )
        return result.scalar_one_or_none()

    async def revoke_if_active(
        self,
        jti_hash: str,
    ) -> RefreshToken | None:
        now = datetime.now(UTC)

        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.jti_hash == jti_hash,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > now,
            )
            .values(revoked_at=now)
            .returning(RefreshToken)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_all_for_user(
        self,
        user_id: UUID,
    ) -> None:
        now = datetime.now(UTC)

        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )

        await self.session.execute(stmt)
