import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.repositories.base import BaseRepository


class WorkspaceRepository(BaseRepository[Workspace]):
    def __init__(self, session: AsyncSession):
        super().__init__(Workspace, session)

    async def get_by_user(
        self,
        offset: int,
        limit: int,
        user_id: uuid.UUID,
    ) -> tuple[list[Workspace], int]:
        member_exists = (
            select(WorkspaceMember.workspace_id)
            .where(
                WorkspaceMember.workspace_id == Workspace.id,
                WorkspaceMember.user_id == user_id,
            )
            .exists()
        )

        condition = or_(
            Workspace.owner_id == user_id,
            member_exists,
        )

        count_stmt = select(func.count()).select_from(Workspace).where(condition)

        total = await self.session.scalar(count_stmt)

        stmt = (
            select(Workspace)
            .where(condition)
            .order_by(
                Workspace.created_at.desc(),
                Workspace.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all()), total or 0
