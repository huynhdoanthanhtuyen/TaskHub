import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentUser, DbSession
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_member_repository import WorkspaceMemberRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.workspace import (
    WorkspaceCreate,
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
) -> WorkspaceService:
    workspace_repository = WorkspaceRepository(session)
    member_repository = WorkspaceMemberRepository(session)
    user_repository = UserRepository(session)

    return WorkspaceService(
        workspace_repository=workspace_repository,
        member_repository=member_repository,
        user_repository=user_repository,
        session=session,
    )


WorkspaceServiceDep = Annotated[
    WorkspaceService,
    Depends(get_workspace_service),
]


@router.post(
    "",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_workspace(
    data: WorkspaceCreate,
    current_user: CurrentUser,
    service: WorkspaceServiceDep,
) -> Workspace:
    return await service.create_workspace(
        data,
        current_user,
    )


@router.get(
    "",
    response_model=list[WorkspaceResponse],
)
async def list_workspaces(
    current_user: CurrentUser,
    service: WorkspaceServiceDep,
) -> list[Workspace]:
    return await service.list_workspaces(current_user)


@router.get(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
)
async def get_workspace(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    service: WorkspaceServiceDep,
) -> Workspace:
    return await service.get_workspace(
        workspace_id,
        current_user,
    )


@router.patch(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
)
async def update_workspace(
    workspace_id: uuid.UUID,
    data: WorkspaceUpdate,
    current_user: CurrentUser,
    service: WorkspaceServiceDep,
) -> Workspace:
    return await service.update_workspace(
        workspace_id,
        data,
        current_user,
    )


@router.delete(
    "/{workspace_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_workspace(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    service: WorkspaceServiceDep,
) -> None:
    await service.delete_workspace(
        workspace_id,
        current_user,
    )


@router.post(
    "/{workspace_id}/members",
    response_model=WorkspaceMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_member(
    workspace_id: uuid.UUID,
    data: WorkspaceMemberCreate,
    current_user: CurrentUser,
    service: WorkspaceServiceDep,
) -> WorkspaceMember:
    return await service.add_member(
        workspace_id,
        data,
        current_user,
    )


@router.get(
    "/{workspace_id}/members",
    response_model=list[WorkspaceMemberResponse],
)
async def list_members(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    service: WorkspaceServiceDep,
) -> list[WorkspaceMember]:
    return await service.list_members(
        workspace_id,
        current_user,
    )


@router.delete(
    "/{workspace_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_member(
    workspace_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: CurrentUser,
    service: WorkspaceServiceDep,
) -> None:
    await service.remove_member(
        workspace_id,
        user_id,
        current_user,
    )
