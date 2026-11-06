from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, status

from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService, task_service

router = APIRouter()


def get_task_service() -> TaskService:
    return task_service


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate, service: TaskServiceDep):
    return service.create_task(task_data)


@router.get("/", response_model=list[TaskResponse])
async def get_tasks(service: TaskServiceDep):
    return service.get_tasks()


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: Annotated[UUID, Path(description="Task UUID")], service: TaskServiceDep
):
    task = service.get_task(task_id)
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: Annotated[UUID, Path(description="Task UUID")],
    task_data: TaskUpdate,
    service: TaskServiceDep,
):
    task = service.update_task(task_id, task_data)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: Annotated[UUID, Path(description="Task UUID")], service: TaskServiceDep
):
    service.delete_task(task_id)
