
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import messages
from app.core.enums import TaskStatus, WorkspaceRole
from app.core.exceptions import (
    PermissionDeniedError,
    RelatedResourceNotFoundError,
    TaskAssigneeNotMemberError,
    TaskNotFoundError,
    WorkspaceNotFoundError,
)
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.task_repository import TaskRepository
from app.repositories.workspace_member_repository import (
    WorkspaceMemberRepository,
)
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(
        self,
        repository: TaskRepository,
        member_repository: WorkspaceMemberRepository,
        session: AsyncSession,
    ):
        self.repository = repository
        self.member_repository = member_repository
        self.session = session

    async def _get_project(self, project_id: UUID) -> Project:
        project = await self.session.get(Project, project_id)

        if project is None:
            raise RelatedResourceNotFoundError(
                "Project",
                project_id,
            )

        return project

    async def _get_workspace(
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

    async def _get_task(self, task_id: UUID) -> Task:
        task = await self.repository.get_by_id(task_id)

        if task is None:
            raise TaskNotFoundError(task_id)

        return task

    async def _get_user_role(
        self,
        workspace: Workspace,
        current_user_id: UUID,
    ) -> WorkspaceRole | None:
        if workspace.owner_id == current_user_id:
            return WorkspaceRole.OWNER

        member = await self.member_repository.get_member(
            workspace.id,
            current_user_id,
        )

        if member is None:
            return None

        return member.role

    async def _require_access(
        self,
        workspace: Workspace,
        current_user_id: UUID,
    ) -> None:
        role = await self._get_user_role(
            workspace,
            current_user_id,
        )

        if role is None:
            raise WorkspaceNotFoundError(workspace.id)

        if role not in (
            WorkspaceRole.OWNER,
            WorkspaceRole.EDITOR,
            WorkspaceRole.VIEWER,
        ):
            raise PermissionDeniedError(
                messages.TASK_PERMISSION_DENIED
            )

    async def _require_manage_permission(
        self,
        workspace: Workspace,
        current_user_id: UUID,
    ) -> None:
        role = await self._get_user_role(
            workspace,
            current_user_id,
        )

        if role is None:
            raise WorkspaceNotFoundError(workspace.id)

        if role not in (
            WorkspaceRole.OWNER,
            WorkspaceRole.EDITOR,
        ):
            raise PermissionDeniedError(
                messages.TASK_PERMISSION_DENIED
            )

    async def _validate_assignee(
        self,
        workspace: Workspace,
        assignee_id: UUID | None,
    ) -> None:
        if assignee_id is None:
            return

        assignee = await self.session.get(User, assignee_id)

        if assignee is None:
            raise RelatedResourceNotFoundError(
                "Assignee",
                assignee_id,
            )

        if workspace.owner_id == assignee_id:
            return

        member = await self.member_repository.get_member(
            workspace.id,
            assignee_id,
        )

        if member is None:
            raise TaskAssigneeNotMemberError()

    async def _get_task_workspace(
        self,
        task: Task,
    ) -> Workspace:
        project = await self._get_project(task.project_id)

        return await self._get_workspace(
            project.workspace_id
        )

    async def create_task(
        self,
        project_id: UUID,
        task_data: TaskCreate,
        current_user_id: UUID,
    ) -> Task:
        project = await self._get_project(project_id)
        workspace = await self._get_workspace(
            project.workspace_id
        )

        await self._require_manage_permission(
            workspace,
            current_user_id,
        )

        await self._validate_assignee(
            workspace,
            task_data.assignee_id,
        )

        task = Task(
            project_id=project_id,
            created_by=current_user_id,
            assignee_id=task_data.assignee_id,
            title=task_data.title,
            description=task_data.description,
            status=TaskStatus.TODO,
            priority=task_data.priority,
            due_date=task_data.due_date,
        )

        try:
            await self.repository.create(task)
            await self.session.commit()
            await self.session.refresh(task)
            return task

        except Exception:
            await self.session.rollback()
            raise

    async def get_tasks_by_project(
        self,
        project_id: UUID,
        current_user_id: UUID,
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[list[Task], int]:
        project = await self._get_project(project_id)
        workspace = await self._get_workspace(
            project.workspace_id
        )

        await self._require_access(
            workspace,
            current_user_id,
        )

        return await self.repository.get_by_project(
            project_id=project_id,
            offset=offset,
            limit=limit,
        )

    async def get_task(
        self,
        task_id: UUID,
        current_user_id: UUID,
    ) -> Task:
        task = await self._get_task(task_id)
        workspace = await self._get_task_workspace(task)

        await self._require_access(
            workspace,
            current_user_id,
        )

        return task

    async def update_task(
        self,
        task_id: UUID,
        task_data: TaskUpdate,
        current_user_id: UUID,
    ) -> Task:
        task = await self._get_task(task_id)
        workspace = await self._get_task_workspace(task)

        await self._require_manage_permission(
            workspace,
            current_user_id,
        )

        update_data = task_data.model_dump(
            exclude_unset=True
        )

        if "assignee_id" in update_data:
            await self._validate_assignee(
                workspace,
                update_data["assignee_id"],
            )

        for field, value in update_data.items():
            setattr(task, field, value)

        try:
            await self.session.commit()
            await self.session.refresh(task)
            return task

        except Exception:
            await self.session.rollback()
            raise

    async def delete_task(
        self,
        task_id: UUID,
        current_user_id: UUID,
    ) -> None:
        task = await self._get_task(task_id)
        workspace = await self._get_task_workspace(task)

        await self._require_manage_permission(
            workspace,
            current_user_id,
        )

        try:
            await self.repository.delete(task)
            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise
