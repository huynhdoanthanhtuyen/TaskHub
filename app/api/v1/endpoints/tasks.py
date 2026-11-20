
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Path,
    Query,
    Response,
    status,
)

from app.api.deps import CurrentUser, DbSession
from app.core.constants import MAX_PAGE_SIZE
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
)
async def create_task(
    project_id: UUID,
    task_data: TaskCreate,
    current_user: CurrentUser,
    service: TaskServiceDep,
):
    return await service.create_task(
        project_id=project_id,
        task_data=task_data,
        current_user_id=current_user.id,
    )


@project_tasks_router.get(
    "",
    response_model=TaskListResponse,
)
async def get_tasks(
    project_id: UUID,
    current_user: CurrentUser,
    service: TaskServiceDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[
        int,
        Query(ge=1, le=MAX_PAGE_SIZE),
    ] = 10,
):
    tasks, total = await service.get_tasks_by_project(
        project_id=project_id,
        current_user_id=current_user.id,
        offset=offset,
        limit=limit,
    )

    return TaskListResponse(
        items=tasks,
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
async def get_task(
    task_id: Annotated[
        UUID,
        Path(description="Task UUID"),
    ],
    current_user: CurrentUser,
    service: TaskServiceDep,
):
    return await service.get_task(
        task_id=task_id,
        current_user_id=current_user.id,
    )


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
)
async def update_task(
    task_id: Annotated[
        UUID,
        Path(description="Task UUID"),
    ],
    task_data: TaskUpdate,
    current_user: CurrentUser,
    service: TaskServiceDep,
):
    return await service.update_task(
        task_id=task_id,
        task_data=task_data,
        current_user_id=current_user.id,
    )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task(
    task_id: Annotated[
        UUID,
        Path(description="Task UUID"),
    ],
    current_user: CurrentUser,
    service: TaskServiceDep,
):
    await service.delete_task(
        task_id=task_id,
        current_user_id=current_user.id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
