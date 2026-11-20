from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession):
        super().__init__(Task, session)

    async def get_by_project(
        self,
        project_id: UUID,
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[list[Task], int]:
        condition = Task.project_id == project_id

        count_stmt = select(func.count()).select_from(Task).where(condition)
        total = await self.session.scalar(count_stmt) or 0

        stmt = (
            select(Task)
            .where(condition)
            .order_by(
                Task.created_at.desc(),
                Task.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all()), total
