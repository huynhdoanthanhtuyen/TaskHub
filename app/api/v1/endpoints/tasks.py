from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import MAX_PAGE_SIZE
from app.db.session import get_db
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter()
# (Day 3):Replace with authenticated user dependency.
DEV_USER_ID = UUID("11111111-1111-4111-8111-111111111111")


def get_dev_user_id() -> UUID:
    return DEV_USER_ID


DevUserIdDep = Annotated[UUID, Depends(get_dev_user_id)]


def get_task_service(session: Annotated[AsyncSession, Depends(get_db)]) -> TaskService:
    repository = TaskRepository(session)
    return TaskService(repository)


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    task_data: TaskCreate,
    service: TaskServiceDep,
    current_user_id: DevUserIdDep,
):
    return await service.create_task(
        task_data=task_data,
        current_user_id=current_user_id,
    )


@router.get("/", response_model=TaskListResponse)
async def get_tasks(
    service: TaskServiceDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = 10,
):
    tasks, total = await service.get_tasks(skip, limit)

    return TaskListResponse(
        items=tasks,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: Annotated[UUID, Path(description="Task UUID")], service: TaskServiceDep
):
    task = await service.get_task(task_id)
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: Annotated[UUID, Path(description="Task UUID")],
    task_data: TaskUpdate,
    service: TaskServiceDep,
):
    task = await service.update_task(task_id, task_data)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: Annotated[UUID, Path(description="Task UUID")], service: TaskServiceDep
):
    await service.delete_task(task_id)
