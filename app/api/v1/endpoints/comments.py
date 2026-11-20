
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.deps import CurrentUser, DbSession
from app.core.constants import MAX_PAGE_SIZE
from app.repositories.comment_repository import CommentRepository
from app.schemas.comment import (
    CommentCreate,
    CommentListResponse,
    CommentResponse,
    CommentUpdate,
)
from app.services.comment_service import CommentService

task_comments_router = APIRouter(
    prefix="/tasks/{task_id}/comments",
    tags=["Comments"],
)

router = APIRouter(
    prefix="/comments",
    tags=["Comments"],
)


def get_comment_service(session: DbSession) -> CommentService:
    return CommentService(
        repository=CommentRepository(session),
        session=session,
    )


CommentServiceDep = Annotated[
    CommentService,
    Depends(get_comment_service),
]


@task_comments_router.post(
    "",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    task_id: UUID,
    data: CommentCreate,
    current_user: CurrentUser,
    service: CommentServiceDep,
):
    return await service.create_comment(
        task_id, data, current_user.id
    )


@task_comments_router.get(
    "",
    response_model=CommentListResponse,
)
async def list_comments(
    task_id: UUID,
    current_user: CurrentUser,
    service: CommentServiceDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[
        int, Query(ge=1, le=MAX_PAGE_SIZE)
    ] = 10,
):
    comments, total = await service.list_comments(
        task_id,
        current_user.id,
        offset,
        limit,
    )

    return CommentListResponse(
        items=comments,
        total=total,
        offset=offset,
        limit=limit,
    )


@router.patch(
    "/{comment_id}",
    response_model=CommentResponse,
)
async def update_comment(
    comment_id: UUID,
    data: CommentUpdate,
    current_user: CurrentUser,
    service: CommentServiceDep,
):
    return await service.update_comment(
        comment_id, data, current_user.id
    )


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    comment_id: UUID,
    current_user: CurrentUser,
    service: CommentServiceDep,
):
    await service.delete_comment(
        comment_id, current_user.id
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
