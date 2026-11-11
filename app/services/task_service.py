from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import TaskNotFoundError
from app.models.task import Task
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(
        self,
        repository: TaskRepository,
        session: AsyncSession,
    ):
        self.repository = repository
        self.session = session

    async def create_task(self, task_data: TaskCreate) -> Task:
        task = Task(
            id=uuid4(),
            project_id=task_data.project_id,
            created_by=task_data.created_by,
            assignee_id=task_data.assignee_id,
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            priority=task_data.priority,
            due_date=task_data.due_date,
        )

        try:
            await self.repository.create(task)
            await self.session.commit()
            await self.session.refresh(task)
        except Exception:
            await self.session.rollback()
            raise

        return task

    async def get_tasks(
        self,
        skip: int = 0,
        limit: int = 10,
    ) -> list[Task]:
        return await self.repository.get_all(skip, limit)

    async def get_task(self, task_id: UUID) -> Task:
        task = await self.repository.get_by_id(task_id)

        if task is None:
            raise TaskNotFoundError(task_id)

        return task

    async def update_task(
        self,
        task_id: UUID,
        task_data: TaskUpdate,
    ) -> Task:
        existing_task = await self.get_task(task_id)
        update_data = task_data.model_dump(exclude_unset=True)

        try:
            updated_task = await self.repository.update(
                existing_task,
                update_data,
            )

            await self.session.commit()
            await self.session.refresh(updated_task)
        except Exception:
            await self.session.rollback()
            raise

        return updated_task

    async def delete_task(self, task_id: UUID) -> None:
        existing_task = await self.get_task(task_id)

        try:
            await self.repository.delete(existing_task)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
