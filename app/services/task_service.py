from uuid import UUID, uuid4

from app.core.exceptions import TaskNotFoundError
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self):
        self._tasks: dict[UUID, Task] = {}

    def create_task(self, task_data: TaskCreate) -> Task:
        task = Task(
            id=uuid4(),
            title=task_data.title,
            description=task_data.description,
            completed=False,
        )

        self._tasks[task.id] = task
        return task

    def get_tasks(self) -> list[Task]:
        return list(self._tasks.values())

    def get_task(self, task_id: UUID) -> Task:
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def update_task(self, task_id: UUID, task_data: TaskUpdate) -> Task:
        existing_task = self.get_task(task_id)
        update_data = task_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing_task, key, value)
        return existing_task

    def delete_task(self, task_id: UUID) -> None:
        self.get_task(task_id)
        del self._tasks[task_id]


task_service = TaskService()
