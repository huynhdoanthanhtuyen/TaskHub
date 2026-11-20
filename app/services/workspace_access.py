
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import messages
from app.core.enums import WorkspaceRole
from app.core.exceptions import (
    PermissionDeniedError,
    ProjectNotFoundError,
    TaskNotFoundError,
    WorkspaceNotFoundError,
)
from app.models.project import Project
from app.models.task import Task
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember


class WorkspaceAccess:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_project(
        self,
        project_id: UUID,
    ) -> Project:
        project = await self.session.get(
            Project,
            project_id,
        )

        if project is None:
            raise ProjectNotFoundError()

        return project

    async def get_task(
        self,
        task_id: UUID,
    ) -> Task:
        task = await self.session.get(
            Task,
            task_id,
        )

        if task is None:
            raise TaskNotFoundError(task_id)

        return task

    async def get_workspace(
        self,
        workspace_id: UUID,
    ) -> Workspace:
        workspace = await self.session.get(
            Workspace,
            workspace_id,
        )

        if workspace is None:
            raise WorkspaceNotFoundError(workspace_id)

        return workspace

    async def get_role(
        self,
        workspace: Workspace,
        user_id: UUID,
    ) -> WorkspaceRole | None:
        if workspace.owner_id == user_id:
            return WorkspaceRole.OWNER

        stmt = select(WorkspaceMember.role).where(
            WorkspaceMember.workspace_id == workspace.id,
            WorkspaceMember.user_id == user_id,
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def require_access(
        self,
        workspace: Workspace,
        user_id: UUID,
        manage: bool = False,
    ) -> WorkspaceRole:
        role = await self.get_role(
            workspace,
            user_id,
        )

        if role is None:
            raise WorkspaceNotFoundError(workspace.id)

        if role not in (
            WorkspaceRole.OWNER,
            WorkspaceRole.EDITOR,
            WorkspaceRole.VIEWER,
        ):
            raise PermissionDeniedError(
                messages.WORKSPACE_ACCESS_DENIED
            )

        if manage and role not in (
            WorkspaceRole.OWNER,
            WorkspaceRole.EDITOR,
        ):
            raise PermissionDeniedError(
                messages.WORKSPACE_ACCESS_DENIED
            )

        return role

    async def project_workspace(
        self,
        project_id: UUID,
    ) -> Workspace:
        project = await self.get_project(project_id)

        return await self.get_workspace(
            project.workspace_id
        )

    async def task_workspace(
        self,
        task: Task,
    ) -> Workspace:
        return await self.project_workspace(
            task.project_id
        )
