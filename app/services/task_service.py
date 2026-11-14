from uuid import UUID, uuid4

from app.core.enums import TaskStatus
from app.core.exceptions import RelatedResourceNotFoundError, TaskNotFoundError
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository
        self.session = repository.session

    async def _validate_task_references(
        self, project_id: UUID, created_by: UUID, assignee_id: UUID | None
    ) -> None:
        project = await self.session.get(Project, project_id)
        if project is None:
            raise RelatedResourceNotFoundError("Project", project_id)
        creator = await self.session.get(User, created_by)
        if creator is None:
            raise RelatedResourceNotFoundError("User", created_by)
        if assignee_id is not None:
            assignee = await self.session.get(User, assignee_id)
            if assignee is None:
                raise RelatedResourceNotFoundError("Assignee", assignee_id)

    async def create_task(self, task_data: TaskCreate, current_user_id: UUID) -> Task:
        await self._validate_task_references(
            project_id=task_data.project_id,
            created_by=current_user_id,
            assignee_id=task_data.assignee_id,
        )
        task = Task(
            id=uuid4(),
            project_id=task_data.project_id,
            created_by=current_user_id,
            assignee_id=task_data.assignee_id,
            title=task_data.title,
            description=task_data.description,
            status=TaskStatus.TODO,
            priority=task_data.priority,
            due_date=task_data.due_date,
        )
        try:
            await self.repository.create(task)
            await self.session.commit()
            await self.session.refresh(task)
            return task
        except Exception:
            await self.session.rollback()
            raise

    async def get_tasks(self, skip: int = 0, limit: int = 10) -> tuple[list[Task], int]:
        return await self.repository.get_all(skip, limit)

    async def get_task(self, task_id: UUID) -> Task:
        task = await self.repository.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    async def update_task(self, task_id: UUID, task_data: TaskUpdate) -> Task:
        existing_task = await self.get_task(task_id)
        update_data = task_data.model_dump(exclude_unset=True)
        if "assignee_id" in update_data:
            assignee_id = update_data["assignee_id"]

            if assignee_id is not None:
                assignee = await self.session.get(User, assignee_id)

                if assignee is None:
                    raise RelatedResourceNotFoundError("Assignee", assignee_id)

        try:
            task = await self.repository.update(existing_task, update_data)
            await self.session.commit()
            await self.session.refresh(task)
            return task
        except Exception:
            await self.session.rollback()
            raise

    async def delete_task(self, task_id: UUID) -> None:
        existing_task = await self.get_task(task_id)
        try:
            await self.repository.delete(existing_task)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
