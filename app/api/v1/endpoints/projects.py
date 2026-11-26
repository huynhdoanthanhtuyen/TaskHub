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
from app.core.enums import ProjectStatus
from app.repositories.project_repository import ProjectRepository
from app.repositories.workspace_member_repository import (
    WorkspaceMemberRepository,
)
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.project_service import ProjectService

workspace_projects_router = APIRouter(
    prefix="/workspaces/{workspace_id}/projects",
    tags=["Projects"],
)

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


def get_project_service(
    session: DbSession,
    cache: CacheDep,
) -> ProjectService:
    return ProjectService(
        project_repository=ProjectRepository(session),
        workspace_repository=WorkspaceRepository(session),
        member_repository=WorkspaceMemberRepository(session),
        session=session,
        cache=cache,
    )


ProjectServiceDep = Annotated[
    ProjectService,
    Depends(get_project_service),
]


@workspace_projects_router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project",
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
async def create_project(
    workspace_id: uuid.UUID,
    data: ProjectCreate,
    current_user: CurrentUser,
    service: ProjectServiceDep,
) -> ProjectResponse:
    project = await service.create_project(
        workspace_id=workspace_id,
        data=data,
        current_user=current_user,
    )

    return ProjectResponse.model_validate(project)


@workspace_projects_router.get(
    "",
    response_model=ProjectListResponse,
    summary="List, search and filter projects in a workspace",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Inactive user",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Workspace not found",
        },
    },
)
async def list_projects(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    service: ProjectServiceDep,
    pagination: PaginationDep,
    searching: SearchDep,
    status: ProjectStatus | None = None,
) -> ProjectListResponse:
    return await service.list_projects(
        workspace_id=workspace_id,
        offset=pagination.offset,
        limit=pagination.limit,
        current_user=current_user,
        status=status,
        search=searching.search,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get project details",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Inactive user",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Project not found",
        },
    },
)
async def get_project(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    service: ProjectServiceDep,
) -> ProjectResponse:
    project = await service.get_project(
        project_id=project_id,
        current_user=current_user,
    )

    return ProjectResponse.model_validate(project)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update a project",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Permission denied",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Project not found",
        },
        status.HTTP_409_CONFLICT: {
            "description": "Project is archived",
        },
    },
)
async def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    current_user: CurrentUser,
    service: ProjectServiceDep,
) -> ProjectResponse:
    project = await service.update_project(
        project_id=project_id,
        data=data,
        current_user=current_user,
    )

    return ProjectResponse.model_validate(project)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Permission denied",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Project not found",
        },
        status.HTTP_409_CONFLICT: {
            "description": "Project has related resources",
        },
    },
)
async def delete_project(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    service: ProjectServiceDep,
) -> None:
    await service.delete_project(
        project_id=project_id,
        current_user=current_user,
    )