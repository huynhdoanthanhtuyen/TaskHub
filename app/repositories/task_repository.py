from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.enums import TaskPriority, TaskStatus
from app.core.exceptions import ProjectNotFoundError
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.repositories.base import BaseRepository
from app.services.workspace_access import require_access


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession):
        super().__init__(Task, session)

    async def get_tasks_by_project(
        self,
        project_id: UUID,
        current_user: User,
        offset: int,
        limit: int,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        assignee_id: UUID | None = None,
    ) -> tuple[list[Task], int]:
        project = await self._get_project(project_id)

        workspace = await self._get_workspace(project.workspace_id)

        await require_access(
            workspace,
            current_user,
            self.member_repository,
            not_found_exc=ProjectNotFoundError,
        )

        return await self.repository.get_by_project(
            project_id=project_id,
            offset=offset,
            limit=limit,
            status=status,
            priority=priority,
            assignee_id=assignee_id,
        )

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
