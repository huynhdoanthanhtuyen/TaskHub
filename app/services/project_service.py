import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import WorkspaceRole
from app.core.exceptions import (
    PermissionDeniedError,
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
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(
        self,
        project_repository: ProjectRepository,
        workspace_repository: WorkspaceRepository,
        member_repository: WorkspaceMemberRepository,
        session: AsyncSession,
    ):
        self.project_repository = project_repository
        self.workspace_repository = workspace_repository
        self.member_repository = member_repository
        self.session = session

    async def _get_workspace(
        self,
        workspace_id: uuid.UUID,
    ) -> Workspace:
        workspace = await self.workspace_repository.get_by_id(workspace_id)

        if workspace is None:
            raise WorkspaceNotFoundError()

        return workspace

    async def _get_project(
        self,
        project_id: uuid.UUID,
    ) -> Project:
        project = await self.project_repository.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError()

        return project

    async def _require_access(
        self,
        workspace: Workspace,
        current_user: User,
    ) -> None:
        if workspace.owner_id == current_user.id:
            return

        member = await self.member_repository.get_member(
            workspace.id,
            current_user.id,
        )

        if member is None:
            raise WorkspaceNotFoundError()

        if member.role not in (
            WorkspaceRole.OWNER,
            WorkspaceRole.EDITOR,
            WorkspaceRole.VIEWER,
        ):
            raise PermissionDeniedError()

    async def _require_manage_project(
        self,
        workspace: Workspace,
        current_user: User,
    ) -> None:
        if workspace.owner_id == current_user.id:
            return

        member = await self.member_repository.get_member(
            workspace.id,
            current_user.id,
        )

        if member is None:
            raise WorkspaceNotFoundError()

        if member.role != WorkspaceRole.EDITOR:
            raise PermissionDeniedError()

    async def create_project(
        self,
        workspace_id: uuid.UUID,
        data: ProjectCreate,
        current_user: User,
    ) -> Project:
        workspace = await self._get_workspace(workspace_id)

        await self._require_manage_project(
            workspace,
            current_user,
        )

        project = Project(
            workspace_id=workspace_id,
            name=data.name,
            description=data.description,
        )

        self.session.add(project)

        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        await self.session.refresh(project)

        return project

    async def list_projects(
        self,
        workspace_id: uuid.UUID,
        offset: int,
        limit: int,
        current_user: User,
    ) -> tuple[list[Project], int]:
        workspace = await self._get_workspace(workspace_id)

        await self._require_access(
            workspace,
            current_user,
        )

        return await self.project_repository.get_by_workspace(
            workspace_id=workspace_id,
            offset=offset,
            limit=limit,
        )

    async def get_project(
        self,
        project_id: uuid.UUID,
        current_user: User,
    ) -> Project:
        project = await self._get_project(project_id)

        workspace = await self._get_workspace(project.workspace_id)

        await self._require_access(
            workspace,
            current_user,
        )

        return project

    async def update_project(
        self,
        project_id: uuid.UUID,
        data: ProjectUpdate,
        current_user: User,
    ) -> Project:
        project = await self._get_project(project_id)

        workspace = await self._get_workspace(project.workspace_id)

        await self._require_manage_project(
            workspace,
            current_user,
        )

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(project, field, value)

        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        await self.session.refresh(project)

        return project

    async def delete_project(
        self,
        project_id: uuid.UUID,
        current_user: User,
    ) -> None:
        project = await self._get_project(project_id)

        workspace = await self._get_workspace(project.workspace_id)

        await self._require_manage_project(
            workspace,
            current_user,
        )

        try:
            await self.session.delete(project)
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise ProjectHasRelatedResourcesError() from exc
