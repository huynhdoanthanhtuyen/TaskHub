import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import (
    CacheDep,
    CurrentUser,
    DbSession,
    PaginationDep,
    SearchDep,
)
from app.core.enums import WorkspaceRole
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_member_repository import (
    WorkspaceMemberRepository,
)
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceListResponse,
    WorkspaceMemberCreate,
    WorkspaceMemberResponse,
    WorkspaceResponse,
    WorkspaceUpdate,
)
from app.services.workspace_service import WorkspaceService

router = APIRouter(
    prefix="/workspaces",
    tags=["Workspaces"],
)


def get_workspace_service(
    session: DbSession,
    cache: CacheDep,
) -> WorkspaceService:
    return WorkspaceService(
        workspace_repository=WorkspaceRepository(session),
        member_repository=WorkspaceMemberRepository(session),
        user_repository=UserRepository(session),
        session=session,
        cache=cache,
    )


WorkspaceServiceDep = Annotated[
    WorkspaceService,
    Depends(get_workspace_service),
]


@router.post(
    "",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a workspace",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Permission denied",
        },
    },
)
async def create_workspace(
    data: WorkspaceCreate,
    current_user: CurrentUser,
    service: WorkspaceServiceDep,
) -> Workspace:
    return await service.create_workspace(
        data=data,
        current_user=current_user,
    )


@router.get(
    "",
    response_model=WorkspaceListResponse,
    summary="List, search and filter user workspaces",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Permission denied",
        },
    },
)
async def list_workspaces(
    current_user: CurrentUser,
    service: WorkspaceServiceDep,
    pagination: PaginationDep,
    searching: SearchDep,
    role: WorkspaceRole | None = None,
) -> WorkspaceListResponse:
    return await service.list_workspaces(
        offset=pagination.offset,
        limit=pagination.limit,
        current_user=current_user,
        role=role,
        search=searching.search,
    )


@router.get(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    summary="Get workspace details",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Permission denied",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Workspace not found",
        },
    },
)
async def get_workspace(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    service: WorkspaceServiceDep,
) -> Workspace:
    return await service.get_workspace(
        workspace_id=workspace_id,
        current_user=current_user,
    )


@router.patch(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    summary="Update a workspace",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Workspace owner required",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Workspace not found",
        },
    },
)
async def update_workspace(
    workspace_id: uuid.UUID,
    data: WorkspaceUpdate,
    current_user: CurrentUser,
    service: WorkspaceServiceDep,
) -> Workspace:
    return await service.update_workspace(
        workspace_id=workspace_id,
        data=data,
        current_user=current_user,
    )


@router.delete(
    "/{workspace_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a workspace",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Workspace owner required",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Workspace not found",
        },
        status.HTTP_409_CONFLICT: {
            "description": "Workspace has related projects",
        },
    },
)
async def delete_workspace(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    service: WorkspaceServiceDep,
) -> None:
    await service.delete_workspace(
        workspace_id=workspace_id,
        current_user=current_user,
    )


@router.post(
    "/{workspace_id}/members",
    response_model=WorkspaceMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a member to a workspace",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid role or cannot invite workspace owner",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Workspace owner required",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Workspace or user not found",
        },
        status.HTTP_409_CONFLICT: {
            "description": "Workspace member already exists",
        },
    },
)
async def add_member(
    workspace_id: uuid.UUID,
    data: WorkspaceMemberCreate,
    current_user: CurrentUser,
    service: WorkspaceServiceDep,
) -> WorkspaceMember:
    return await service.add_member(
        workspace_id=workspace_id,
        data=data,
        current_user=current_user,
    )


@router.get(
    "/{workspace_id}/members",
    response_model=list[WorkspaceMemberResponse],
    summary="List workspace members",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Permission denied",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Workspace not found",
        },
    },
)
async def list_members(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    service: WorkspaceServiceDep,
) -> list[WorkspaceMember]:
    return await service.list_members(
        workspace_id=workspace_id,
        current_user=current_user,
    )


@router.delete(
    "/{workspace_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a member from a workspace",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Workspace owner cannot be removed",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Workspace owner required",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Workspace or member not found",
        },
    },
)
async def remove_member(
    workspace_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: CurrentUser,
    service: WorkspaceServiceDep,
) -> None:
    await service.remove_member(
        workspace_id=workspace_id,
        user_id=user_id,
        current_user=current_user,
    )