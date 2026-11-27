from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Path,
    status,
)

from app.api.deps import (
    CurrentUser,
    DbSession,
    PaginationDep,
    SearchDep,
)
from app.core.enums import TaskPriority, TaskStatus
from app.repositories.task_repository import TaskRepository
from app.repositories.workspace_member_repository import (
    WorkspaceMemberRepository,
)
from app.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)
from app.services.task_service import TaskService

project_tasks_router = APIRouter(
    prefix="/projects/{project_id}/tasks",
    tags=["Tasks"],
)

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


def get_task_service(session: DbSession) -> TaskService:
    return TaskService(
        repository=TaskRepository(session),
        member_repository=WorkspaceMemberRepository(session),
        session=session,
    )


TaskServiceDep = Annotated[
    TaskService,
    Depends(get_task_service),
]


@project_tasks_router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid assignee"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required"},
        status.HTTP_403_FORBIDDEN: {"description": "Permission denied"},
        status.HTTP_404_NOT_FOUND: {"description": "Project not found"},
        status.HTTP_409_CONFLICT: {"description": "Project is archived"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
    },
)
async def create_task(
    project_id: UUID,
    task_data: TaskCreate,
    current_user: CurrentUser,
    service: TaskServiceDep,
) -> TaskResponse:
    task = await service.create_task(
        project_id=project_id,
        task_data=task_data,
        current_user=current_user,
    )

    return TaskResponse.model_validate(task)


@project_tasks_router.get(
    "",
    response_model=TaskListResponse,
    summary="List, search and filter tasks in a project",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required"},
        status.HTTP_403_FORBIDDEN: {"description": "Inactive user"},
        status.HTTP_404_NOT_FOUND: {"description": "Project not found"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
    },
)
async def get_tasks(
    project_id: UUID,
    current_user: CurrentUser,
    service: TaskServiceDep,
    pagination: PaginationDep,
    searching: SearchDep,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    assignee_id: UUID | None = None,
) -> TaskListResponse:
    tasks, total = await service.get_tasks_by_project(
        project_id=project_id,
        current_user=current_user,
        offset=pagination.offset,
        limit=pagination.limit,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        search=searching.search,
    )

    return TaskListResponse(
        items=[TaskResponse.model_validate(task) for task in tasks],
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get task details",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required"},
        status.HTTP_403_FORBIDDEN: {"description": "Inactive user"},
        status.HTTP_404_NOT_FOUND: {"description": "Task not found"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
    },
)
async def get_task(
    task_id: Annotated[
        UUID,
        Path(description="Task UUID"),
    ],
    current_user: CurrentUser,
    service: TaskServiceDep,
) -> TaskResponse:
    task = await service.get_task(
        task_id=task_id,
        current_user=current_user,
    )

    return TaskResponse.model_validate(task)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid assignee"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required"},
        status.HTTP_403_FORBIDDEN: {"description": "Permission denied"},
        status.HTTP_404_NOT_FOUND: {"description": "Task not found"},
        status.HTTP_409_CONFLICT: {"description": "Project is archived"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
    },
)
async def update_task(
    task_id: Annotated[
        UUID,
        Path(description="Task UUID"),
    ],
    task_data: TaskUpdate,
    current_user: CurrentUser,
    service: TaskServiceDep,
) -> TaskResponse:
    task = await service.update_task(
        task_id=task_id,
        task_data=task_data,
        current_user=current_user,
    )

    return TaskResponse.model_validate(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required"},
        status.HTTP_403_FORBIDDEN: {"description": "Permission denied"},
        status.HTTP_404_NOT_FOUND: {"description": "Task not found"},
        status.HTTP_409_CONFLICT: {"description": "Project is archived"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
    },
)
async def delete_task(
    task_id: Annotated[
        UUID,
        Path(description="Task UUID"),
    ],
    current_user: CurrentUser,
    service: TaskServiceDep,
) -> None:
    await service.delete_task(
        task_id=task_id,
        current_user=current_user,
    )
