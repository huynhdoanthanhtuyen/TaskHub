from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.enums import TaskPriority, TaskStatus
from app.models.project import Project
from app.models.task import Task
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession):
        super().__init__(Task, session)

    async def get_by_project(
        self,
        project_id: UUID,
        offset: int,
        limit: int,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        assignee_id: UUID | None = None,
        search: str | None = None,
    ) -> tuple[list[Task], int]:
        conditions = [
            Task.project_id == project_id,
        ]

        if status is not None:
            conditions.append(Task.status == status)

        if priority is not None:
            conditions.append(Task.priority == priority)

        if assignee_id is not None:
            conditions.append(Task.assignee_id == assignee_id)

        if search:
            conditions.append(
                or_(
                    Task.title.icontains(
                        search,
                        autoescape=True,
                    ),
                    Task.description.icontains(
                        search,
                        autoescape=True,
                    ),
                )
            )

        count_stmt = select(func.count()).select_from(Task).where(*conditions)

        total = await self.session.scalar(count_stmt) or 0

        stmt = (
            select(Task)
            .where(*conditions)
            .order_by(
                Task.created_at.desc(),
                Task.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all()), total

    async def get_by_id_with_project_workspace(
        self,
        task_id: UUID,
    ) -> Task | None:
        stmt = (
            select(Task)
            .options(joinedload(Task.project).joinedload(Project.workspace))
            .where(Task.id == task_id)
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()
