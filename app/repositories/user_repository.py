from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ADMIN_MANAGEMENT_LOCK_ID
from app.core.enums import UserRole
from app.models.admin_management_lock import AdminManagementLock
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_paginated(
        self,
        offset: int,
        limit: int,
    ) -> list[User]:
        result = await self.session.execute(
            select(User)
            .order_by(User.created_at.desc(), User.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())


    async def count_users(self) -> int:
        result = await self.session.execute(
            select(func.count(User.id))
        )
        return result.scalar_one()

    async def lock_admin_management(self) -> None:
        result = await self.session.execute(
            select(AdminManagementLock)
            .where(AdminManagementLock.id == ADMIN_MANAGEMENT_LOCK_ID)
            .with_for_update()
        )

        if result.scalar_one_or_none() is None:
            raise RuntimeError("Admin management lock record not found")

    async def get_by_id_fresh(self, user_id: UUID) -> User | None:
        result = await self.session.execute(
            select(User)
            .where(User.id == user_id)
            .execution_options(populate_existing=True)
        )
        return result.scalar_one_or_none()

    async def count_active_admins(self) -> int:
        result = await self.session.execute(
            select(func.count(User.id)).where(
                User.role == UserRole.ADMIN,
                User.is_active.is_(True),
            )
        )
        return result.scalar_one()
