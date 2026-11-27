from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import CurrentUser, DbSession, PaginationDep, SearchDep
from app.repositories.comment_repository import CommentRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.workspace_member_repository import (
    WorkspaceMemberRepository,
)
from app.schemas.comment import (
    CommentCreate,
    CommentFilter,
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
        task_repository=TaskRepository(session),
        member_repository=WorkspaceMemberRepository(session),
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
    summary="Create a comment",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required"},
        status.HTTP_403_FORBIDDEN: {"description": "Permission denied"},
        status.HTTP_404_NOT_FOUND: {"description": "Task not found"},
    },
)
async def create_comment(
    task_id: UUID,
    data: CommentCreate,
    current_user: CurrentUser,
    service: CommentServiceDep,
) -> CommentResponse:
    comment = await service.create_comment(
        task_id=task_id,
        data=data,
        current_user=current_user,
    )

    return CommentResponse.model_validate(comment)


@task_comments_router.get(
    "",
    response_model=CommentListResponse,
    summary="List, search and filter comments in a task",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required"},
        status.HTTP_403_FORBIDDEN: {"description": "Permission denied"},
        status.HTTP_404_NOT_FOUND: {"description": "Task not found"},
    },
)
async def list_comments(
    task_id: UUID,
    current_user: CurrentUser,
    service: CommentServiceDep,
    pagination: PaginationDep,
    searching: SearchDep,
    filters: Annotated[CommentFilter, Query()],
) -> CommentListResponse:
    comments, total = await service.list_comments(
        task_id=task_id,
        current_user=current_user,
        offset=pagination.offset,
        limit=pagination.limit,
        search=searching.search,
        author_id=filters.author_id,
        created_from=filters.created_from,
        created_to=filters.created_to,
    )

    return CommentListResponse(
        items=[CommentResponse.model_validate(comment) for comment in comments],
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
    )


@router.patch(
    "/{comment_id}",
    response_model=CommentResponse,
    summary="Update a comment",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required"},
        status.HTTP_403_FORBIDDEN: {
            "description": "Permission denied or not the comment author"
        },
        status.HTTP_404_NOT_FOUND: {"description": "Comment not found"},
    },
)
async def update_comment(
    comment_id: UUID,
    data: CommentUpdate,
    current_user: CurrentUser,
    service: CommentServiceDep,
) -> CommentResponse:
    comment = await service.update_comment(
        comment_id=comment_id,
        data=data,
        current_user=current_user,
    )

    return CommentResponse.model_validate(comment)


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a comment",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required"},
        status.HTTP_403_FORBIDDEN: {"description": "Permission denied"},
        status.HTTP_404_NOT_FOUND: {"description": "Comment not found"},
    },
)
async def delete_comment(
    comment_id: UUID,
    current_user: CurrentUser,
    service: CommentServiceDep,
) -> None:
    await service.delete_comment(
        comment_id=comment_id,
        current_user=current_user,
    )
