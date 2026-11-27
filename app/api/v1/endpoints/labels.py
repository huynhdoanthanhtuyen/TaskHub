from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import CurrentUser, DbSession, PaginationDep, SearchDep
from app.core.constants import LABEL_COLOR_MAX_LENGTH, LABEL_COLOR_PATTERN
from app.repositories.label_repository import LabelRepository
from app.repositories.task_label_repository import TaskLabelRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.workspace_member_repository import (
    WorkspaceMemberRepository,
)
from app.schemas.label import (
    LabelCreate,
    LabelListResponse,
    LabelResponse,
    LabelUpdate,
)
from app.services.label_service import LabelService

project_labels_router = APIRouter(
    prefix="/projects/{project_id}/labels",
    tags=["Labels"],
)

router = APIRouter(
    prefix="/labels",
    tags=["Labels"],
)

task_labels_router = APIRouter(
    prefix="/tasks/{task_id}/labels",
    tags=["Labels"],
)


def get_label_service(session: DbSession) -> LabelService:
    return LabelService(
        repository=LabelRepository(session),
        task_label_repository=TaskLabelRepository(session),
        task_repository=TaskRepository(session),
        member_repository=WorkspaceMemberRepository(session),
        session=session,
    )


LabelServiceDep = Annotated[
    LabelService,
    Depends(get_label_service),
]


@project_labels_router.post(
    "",
    response_model=LabelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a label",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required"},
        status.HTTP_403_FORBIDDEN: {"description": "Permission denied"},
        status.HTTP_404_NOT_FOUND: {"description": "Project not found"},
        status.HTTP_409_CONFLICT: {
            "description": "Label name already exists in the project"
        },
    },
)
async def create_label(
    project_id: UUID,
    data: LabelCreate,
    current_user: CurrentUser,
    service: LabelServiceDep,
) -> LabelResponse:
    label = await service.create_label(
        project_id=project_id,
        data=data,
        current_user=current_user,
    )

    return LabelResponse.model_validate(label)


@project_labels_router.get(
    "",
    response_model=LabelListResponse,
    summary="List, search and filter labels in a project",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required"},
        status.HTTP_403_FORBIDDEN: {"description": "Permission denied"},
        status.HTTP_404_NOT_FOUND: {"description": "Project not found"},
    },
)
async def list_labels(
    project_id: UUID,
    current_user: CurrentUser,
    service: LabelServiceDep,
    pagination: PaginationDep,
    searching: SearchDep,
    color: str | None = Query(
        default=None,
        max_length=LABEL_COLOR_MAX_LENGTH,
        pattern=LABEL_COLOR_PATTERN,
        description="Filter labels by HEX color",
    ),
) -> LabelListResponse:
    labels, total = await service.list_labels(
        project_id=project_id,
        current_user=current_user,
        offset=pagination.offset,
        limit=pagination.limit,
        search=searching.search,
        color=color,
    )

    return LabelListResponse(
        items=[LabelResponse.model_validate(label) for label in labels],
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
    )


@router.patch(
    "/{label_id}",
    response_model=LabelResponse,
    summary="Update a label",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required"},
        status.HTTP_403_FORBIDDEN: {"description": "Permission denied"},
        status.HTTP_404_NOT_FOUND: {"description": "Label not found"},
        status.HTTP_409_CONFLICT: {
            "description": "Label name already exists in the project"
        },
    },
)
async def update_label(
    label_id: UUID,
    data: LabelUpdate,
    current_user: CurrentUser,
    service: LabelServiceDep,
) -> LabelResponse:
    label = await service.update_label(
        label_id=label_id,
        data=data,
        current_user=current_user,
    )

    return LabelResponse.model_validate(label)


@router.delete(
    "/{label_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a label",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required"},
        status.HTTP_403_FORBIDDEN: {"description": "Permission denied"},
        status.HTTP_404_NOT_FOUND: {"description": "Label not found"},
    },
)
async def delete_label(
    label_id: UUID,
    current_user: CurrentUser,
    service: LabelServiceDep,
) -> None:
    await service.delete_label(
        label_id=label_id,
        current_user=current_user,
    )


@task_labels_router.get(
    "",
    response_model=LabelListResponse,
    summary="List, search and filter labels attached to a task",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required"},
        status.HTTP_403_FORBIDDEN: {"description": "Permission denied"},
        status.HTTP_404_NOT_FOUND: {"description": "Task not found"},
    },
)
async def list_task_labels(
    task_id: UUID,
    current_user: CurrentUser,
    service: LabelServiceDep,
    pagination: PaginationDep,
    searching: SearchDep,
    color: str | None = Query(
        default=None,
        max_length=LABEL_COLOR_MAX_LENGTH,
        pattern=LABEL_COLOR_PATTERN,
        description="Filter labels by HEX color",
    ),
) -> LabelListResponse:
    labels, total = await service.list_labels_by_task(
        task_id=task_id,
        current_user=current_user,
        offset=pagination.offset,
        limit=pagination.limit,
        search=searching.search,
        color=color,
    )

    return LabelListResponse(
        items=[LabelResponse.model_validate(label) for label in labels],
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
    )


@task_labels_router.post(
    "/{label_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Attach a label to a task",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Label and task belong to different projects"
        },
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required"},
        status.HTTP_403_FORBIDDEN: {"description": "Permission denied"},
        status.HTTP_404_NOT_FOUND: {"description": "Task or label not found"},
        status.HTTP_409_CONFLICT: {"description": "Label already attached"},
    },
)
async def attach_label(
    task_id: UUID,
    label_id: UUID,
    current_user: CurrentUser,
    service: LabelServiceDep,
) -> None:
    await service.attach_label(
        task_id=task_id,
        label_id=label_id,
        current_user=current_user,
    )


@task_labels_router.delete(
    "/{label_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Detach a label from a task",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required"},
        status.HTTP_403_FORBIDDEN: {"description": "Permission denied"},
        status.HTTP_404_NOT_FOUND: {
            "description": "Task, label or attachment not found"
        },
    },
)
async def detach_label(
    task_id: UUID,
    label_id: UUID,
    current_user: CurrentUser,
    service: LabelServiceDep,
) -> None:
    await service.detach_label(
        task_id=task_id,
        label_id=label_id,
        current_user=current_user,
    )
