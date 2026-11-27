import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import ProjectStatus
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
        status: ProjectStatus | None = None,
        search: str | None = None,
    ) -> tuple[list[Project], int]:
        conditions = [Project.workspace_id == workspace_id]

        if status is not None:
            conditions.append(Project.status == status)

        if search:
            conditions.append(Project.name.icontains(search, autoescape=True))

        count_stmt = select(func.count()).select_from(Project).where(*conditions)

        total = await self.session.scalar(count_stmt) or 0

        stmt = (
            select(Project)
            .where(*conditions)
            .order_by(
                Project.created_at.desc(),
                Project.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all()), total
