import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.keys import CacheKey
from app.cache.service import CacheService
from app.core.constants import PROJECT_MANAGE_ROLES
from app.core.enums import ProjectStatus
from app.core.exceptions import (
    ProjectArchivedError,
    ProjectHasRelatedResourcesError,
    ProjectNotFoundError,
    WorkspaceNotFoundError,
)
from app.models.project import Project
from app.models.user import User
from app.models.workspace import Workspace
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
from app.services.workspace_access import require_access


class ProjectService:
    def __init__(
        self,
        project_repository: ProjectRepository,
        workspace_repository: WorkspaceRepository,
        member_repository: WorkspaceMemberRepository,
        session: AsyncSession,
        cache: CacheService,
    ):
        self.project_repository = project_repository
        self.workspace_repository = workspace_repository
        self.member_repository = member_repository
        self.session = session
        self.cache = cache

    async def _get_workspace(
        self,
        workspace_id: uuid.UUID,
    ) -> Workspace:
        workspace = await self.workspace_repository.get_by_id(
            workspace_id,
        )

        if workspace is None:
            raise WorkspaceNotFoundError()

        return workspace

    async def _get_project(
        self,
        project_id: uuid.UUID,
    ) -> Project:
        project = await self.project_repository.get_by_id(
            project_id,
        )

        if project is None:
            raise ProjectNotFoundError()

        return project

    async def _invalidate_project_cache(
        self,
        workspace_id: uuid.UUID,
    ) -> None:
        pattern = CacheKey.pattern(
            resource="projects",
            scope=workspace_id,
            operation="list",
        )

        await self.cache.invalidate(pattern)

    async def create_project(
        self,
        workspace_id: uuid.UUID,
        data: ProjectCreate,
        current_user: User,
    ) -> Project:
        workspace = await self._get_workspace(workspace_id)

        await require_access(
            workspace,
            current_user,
            self.member_repository,
            allowed_roles=PROJECT_MANAGE_ROLES,
        )

        project = Project(
            workspace_id=workspace_id,
            name=data.name,
            description=data.description,
        )

        await self.project_repository.create(project)

        await self.session.commit()

        await self._invalidate_project_cache(
            workspace_id,
        )

        await self.session.refresh(project)

        return project

    async def list_projects(
        self,
        workspace_id: uuid.UUID,
        offset: int,
        limit: int,
        current_user: User,
        status: ProjectStatus | None = None,
        search: str | None = None,
    ) -> ProjectListResponse:
        workspace = await self._get_workspace(workspace_id)

        await require_access(
            workspace,
            current_user,
            self.member_repository,
        )

        cache_key = CacheKey.build(
            resource="projects",
            scope=workspace_id,
            operation="list",
            user_id=current_user.id,
            offset=offset,
            limit=limit,
            status=status,
            search=search,
        )

        cached_response = await self.cache.get(
            cache_key,
            ProjectListResponse,
        )

        if cached_response is not None:
            return cached_response

        projects, total = (
            await self.project_repository.get_by_workspace(
                workspace_id=workspace_id,
                offset=offset,
                limit=limit,
                status=status,
                search=search,
            )
        )

        response = ProjectListResponse(
            items=[
                ProjectResponse.model_validate(project)
                for project in projects
            ],
            total=total,
            offset=offset,
            limit=limit,
        )

        await self.cache.set(
            cache_key,
            response,
        )

        return response

    async def get_project(
        self,
        project_id: uuid.UUID,
        current_user: User,
    ) -> Project:
        project = await self._get_project(project_id)

        workspace = await self._get_workspace(
            project.workspace_id,
        )

        await require_access(
            workspace,
            current_user,
            self.member_repository,
            not_found_exc=ProjectNotFoundError,
        )

        return project

    async def update_project(
        self,
        project_id: uuid.UUID,
        data: ProjectUpdate,
        current_user: User,
    ) -> Project:
        project = await self._get_project(project_id)

        workspace = await self._get_workspace(
            project.workspace_id,
        )

        await require_access(
            workspace,
            current_user,
            self.member_repository,
            allowed_roles=PROJECT_MANAGE_ROLES,
            not_found_exc=ProjectNotFoundError,
        )

        update_data = data.model_dump(
            exclude_unset=True,
        )

        if project.status == ProjectStatus.ARCHIVED and (
            update_data.keys() != {"status"}
            or update_data.get("status") != ProjectStatus.ACTIVE
        ):
            raise ProjectArchivedError()

        for field, value in update_data.items():
            setattr(project, field, value)

        workspace_id = project.workspace_id

        await self.session.commit()

        await self._invalidate_project_cache(
            workspace_id,
        )

        await self.session.refresh(project)

        return project

    async def delete_project(
        self,
        project_id: uuid.UUID,
        current_user: User,
    ) -> None:
        project = await self._get_project(project_id)

        workspace = await self._get_workspace(
            project.workspace_id,
        )

        await require_access(
            workspace,
            current_user,
            self.member_repository,
            allowed_roles=PROJECT_MANAGE_ROLES,
            not_found_exc=ProjectNotFoundError,
        )

        workspace_id = project.workspace_id

        try:
            await self.project_repository.delete(project)
            await self.session.commit()

        except IntegrityError as exc:
            await self.session.rollback()
            raise ProjectHasRelatedResourcesError() from exc

        await self._invalidate_project_cache(
            workspace_id,
        )