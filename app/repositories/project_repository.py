import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, session: AsyncSession):
        super().__init__(Project, session)

    async def get_by_workspace(
        self,
        workspace_id: uuid.UUID,
        offset: int,
        limit: int,
    ) -> tuple[list[Project], int]:
        condition = Project.workspace_id == workspace_id

        count_stmt = select(func.count()).select_from(Project).where(condition)

        total = await self.session.scalar(count_stmt) or 0

        stmt = (
            select(Project)
            .where(condition)
            .order_by(
                Project.created_at.desc(),
                Project.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all()), total
