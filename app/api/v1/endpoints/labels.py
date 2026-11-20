
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.deps import CurrentUser, DbSession
from app.core.constants import MAX_PAGE_SIZE
from app.repositories.label_repository import LabelRepository
from app.repositories.task_label_repository import TaskLabelRepository
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
)
async def create_label(
    project_id: UUID,
    data: LabelCreate,
    current_user: CurrentUser,
    service: LabelServiceDep,
):
    return await service.create_label(
        project_id, data, current_user.id
    )


@project_labels_router.get(
    "",
    response_model=LabelListResponse,
)
async def list_labels(
    project_id: UUID,
    current_user: CurrentUser,
    service: LabelServiceDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[
        int, Query(ge=1, le=MAX_PAGE_SIZE)
    ] = 10,
):
    labels, total = await service.list_labels(
        project_id,
        current_user.id,
        offset,
        limit,
    )

    return LabelListResponse(
        items=labels,
        total=total,
        offset=offset,
        limit=limit,
    )


@router.patch(
    "/{label_id}",
    response_model=LabelResponse,
)
async def update_label(
    label_id: UUID,
    data: LabelUpdate,
    current_user: CurrentUser,
    service: LabelServiceDep,
):
    return await service.update_label(
        label_id, data, current_user.id
    )


@router.delete(
    "/{label_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_label(
    label_id: UUID,
    current_user: CurrentUser,
    service: LabelServiceDep,
):
    await service.delete_label(label_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@task_labels_router.post(
    "/{label_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def attach_label(
    task_id: UUID,
    label_id: UUID,
    current_user: CurrentUser,
    service: LabelServiceDep,
):
    await service.attach_label(
        task_id, label_id, current_user.id
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@task_labels_router.delete(
    "/{label_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def detach_label(
    task_id: UUID,
    label_id: UUID,
    current_user: CurrentUser,
    service: LabelServiceDep,
):
    await service.detach_label(
        task_id, label_id, current_user.id
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
