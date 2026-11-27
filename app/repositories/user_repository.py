from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ADMIN_MANAGEMENT_LOCK_ID
from app.core.enums import UserRole
from app.models.admin_management_lock import AdminManagementLock
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))

        return result.scalar_one_or_none()

    async def get_paginated(
        self,
        offset: int,
        limit: int,
        role: UserRole | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> tuple[list[User], int]:
        conditions = []

        if role is not None:
            conditions.append(User.role == role)

        if is_active is not None:
            conditions.append(User.is_active.is_(is_active))

        if search:
            conditions.append(
                or_(
                    User.full_name.icontains(
                        search,
                        autoescape=True,
                    ),
                    User.email.icontains(
                        search,
                        autoescape=True,
                    ),
                )
            )

        count_stmt = select(func.count()).select_from(User).where(*conditions)

        total = await self.session.scalar(count_stmt) or 0

        stmt = (
            select(User)
            .where(*conditions)
            .order_by(
                User.created_at.desc(),
                User.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all()), total

    async def lock_admin_management(self) -> None:
        result = await self.session.execute(
            select(AdminManagementLock)
            .where(AdminManagementLock.id == ADMIN_MANAGEMENT_LOCK_ID)
            .with_for_update()
        )

        if result.scalar_one_or_none() is None:
            raise RuntimeError("Admin management lock record not found")

    async def get_by_id_fresh(
        self,
        user_id: UUID,
    ) -> User | None:
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
