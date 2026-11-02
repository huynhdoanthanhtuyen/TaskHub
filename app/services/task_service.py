from uuid import UUID, uuid4
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse

class TaskService:
  def __init__(self):
    self._tasks: dict[UUID, TaskResponse] ={}

  def create_task(self, task_data: TaskCreate) -> TaskResponse:
    task = TaskResponse(
      id = uuid4(),
      title = task_data.title,
      description= task_data.description,
      completed= False
    )

    self._tasks[task.id]= task
    return task


  def get_tasks(self) -> list[TaskResponse]:
    return list(self._tasks.values())

  def get_task(self, task_id: UUID) -> TaskResponse|None:
    return self._tasks.get(task_id)

  def update_task(self, task_id:UUID, task_data: TaskUpdate) -> TaskResponse|None:
    existing_task = self._tasks.get(task_id)
    if existing_task is None:
      return None
    update_data = task_data.model_dump(exclude_unset=True)
    update_task = existing_task.model_copy(update= update_data)
    self._tasks[task_id]= update_task
    return update_task

  def delete_task(self, task_id: UUID) -> bool:
    if task_id not in self._tasks:
      return False
    del self._tasks[task_id]
    return True

task_service = TaskService()