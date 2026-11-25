import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import CurrentUser, DbSession, PaginationDep
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


def get_project_service(session: DbSession) -> ProjectService:
    return ProjectService(
        project_repository=ProjectRepository(session),
        workspace_repository=WorkspaceRepository(session),
        member_repository=WorkspaceMemberRepository(session),
        session=session,
    )


ProjectServiceDep = Annotated[
    ProjectService,
    Depends(get_project_service),
]


@workspace_projects_router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    workspace_id: uuid.UUID,
    data: ProjectCreate,
    current_user: CurrentUser,
    service: ProjectServiceDep,
):
    return await service.create_project(
        workspace_id=workspace_id,
        data=data,
        current_user=current_user,
    )


@workspace_projects_router.get(
    "",
    response_model=ProjectListResponse,
)
async def list_projects(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    service: ProjectServiceDep,
    pagination: PaginationDep,
):
    projects, total = await service.list_projects(
        workspace_id=workspace_id,
        offset=pagination.offset,
        limit=pagination.limit,
        current_user=current_user,
    )

    return ProjectListResponse(
        items=projects,
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
async def get_project(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    service: ProjectServiceDep,
):
    return await service.get_project(
        project_id=project_id,
        current_user=current_user,
    )


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
)
async def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    current_user: CurrentUser,
    service: ProjectServiceDep,
):
    return await service.update_project(
        project_id=project_id,
        data=data,
        current_user=current_user,
    )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_project(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    service: ProjectServiceDep,
):
    await service.delete_project(
        project_id=project_id,
        current_user=current_user,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
