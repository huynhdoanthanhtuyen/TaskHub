from uuid import UUID, uuid4
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.repositories.task_repository import TaskRepository
from app.models.task import Task

class TaskService:
  def __init__(self, repository: TaskRepository):
    self.repository = repository

  async def create_task(self, task_data: TaskCreate) -> TaskResponse:
    task = Task(
      id = uuid4(),
      title = task_data.title,
      description= task_data.description,
      completed= False
    )

    await self.repository.create(task)
    return task


  async def get_tasks(self,skip:int=0, limit:int=10) -> list[TaskResponse]:
    return await self.repository.get_all(skip,limit)

  async def get_task(self, task_id: UUID) -> TaskResponse|None:
    return await self.repository.get_by_id(task_id)

  async def update_task(self, task_id:UUID, task_data: TaskUpdate) -> TaskResponse|None:
    existing_task = await self.repository.get_by_id(task_id)
    if existing_task is None:
      return None
    update_data = task_data.model_dump(exclude_unset=True)
    return await self.repository.update(existing_task,update_data)

  async def delete_task(self, task_id: UUID) -> bool:
    existing_task = await self.repository.get_by_id(task_id)
    if existing_task is None:
      return False
    await self.repository.delete(existing_task)
    return True