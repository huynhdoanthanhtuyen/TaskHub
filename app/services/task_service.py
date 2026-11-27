from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import TASK_MANAGE_ROLES
from app.core.enums import ProjectStatus, TaskPriority, TaskStatus
from app.core.exceptions import (
    ProjectArchivedError,
    ProjectNotFoundError,
    TaskAssigneeInactiveError,
    TaskAssigneeNotFoundError,
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
from app.services.workspace_access import require_access


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
            raise ProjectNotFoundError()

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
            raise WorkspaceNotFoundError()

        return workspace

    async def _get_task(
        self,
        task_id: UUID,
    ) -> Task:
        task = await self.repository.get_by_id_with_project_workspace(task_id)

        if task is None:
            raise TaskNotFoundError()

        return task

    def _get_task_workspace(
        self,
        task: Task,
    ) -> tuple[Project, Workspace]:
        return task.project, task.project.workspace

    def _require_active_project(
        self,
        project: Project,
    ) -> None:
        if project.status == ProjectStatus.ARCHIVED:
            raise ProjectArchivedError()

    async def _validate_assignee(
        self,
        workspace: Workspace,
        assignee_id: UUID | None,
    ) -> None:
        if assignee_id is None:
            return

        assignee = await self.session.get(
            User,
            assignee_id,
        )

        if assignee is None:
            raise TaskAssigneeNotFoundError()

        if not assignee.is_active:
            raise TaskAssigneeInactiveError()

        if workspace.owner_id == assignee_id:
            return

        member = await self.member_repository.get_member(
            workspace.id,
            assignee_id,
        )

        if member is None:
            raise TaskAssigneeNotMemberError()

    async def create_task(
        self,
        project_id: UUID,
        task_data: TaskCreate,
        current_user: User,
    ) -> Task:
        project = await self._get_project(project_id)
        workspace = await self._get_workspace(project.workspace_id)

        await require_access(
            workspace,
            current_user,
            self.member_repository,
            allowed_roles=TASK_MANAGE_ROLES,
            not_found_exc=ProjectNotFoundError,
        )

        self._require_active_project(project)

        await self._validate_assignee(
            workspace,
            task_data.assignee_id,
        )

        task = Task(
            project_id=project_id,
            created_by=current_user.id,
            assignee_id=task_data.assignee_id,
            title=task_data.title,
            description=task_data.description,
            status=TaskStatus.TODO,
            priority=task_data.priority,
            due_date=task_data.due_date,
        )

        await self.repository.create(task)
        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def get_tasks_by_project(
        self,
        project_id: UUID,
        current_user: User,
        offset: int,
        limit: int,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        assignee_id: UUID | None = None,
        search: str | None = None,
    ) -> tuple[list[Task], int]:
        project = await self._get_project(project_id)

        workspace = await self._get_workspace(project.workspace_id)

        await require_access(
            workspace,
            current_user,
            self.member_repository,
            not_found_exc=ProjectNotFoundError,
        )

        return await self.repository.get_by_project(
            project_id=project_id,
            offset=offset,
            limit=limit,
            status=status,
            priority=priority,
            assignee_id=assignee_id,
            search=search,
        )

    async def get_task(
        self,
        task_id: UUID,
        current_user: User,
    ) -> Task:
        task = await self._get_task(task_id)

        _, workspace = self._get_task_workspace(task)

        await require_access(
            workspace,
            current_user,
            self.member_repository,
            not_found_exc=TaskNotFoundError,
        )

        return task

    async def update_task(
        self,
        task_id: UUID,
        task_data: TaskUpdate,
        current_user: User,
    ) -> Task:
        task = await self._get_task(task_id)

        project, workspace = self._get_task_workspace(task)

        await require_access(
            workspace,
            current_user,
            self.member_repository,
            allowed_roles=TASK_MANAGE_ROLES,
            not_found_exc=TaskNotFoundError,
        )

        self._require_active_project(project)

        update_data = task_data.model_dump(exclude_unset=True)

        if "assignee_id" in update_data:
            await self._validate_assignee(
                workspace,
                update_data["assignee_id"],
            )

        await self.repository.update(task, update_data)

        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def delete_task(
        self,
        task_id: UUID,
        current_user: User,
    ) -> None:
        task = await self._get_task(task_id)
        project, workspace = self._get_task_workspace(task)

        await require_access(
            workspace,
            current_user,
            self.member_repository,
            allowed_roles=TASK_MANAGE_ROLES,
            not_found_exc=TaskNotFoundError,
        )

        self._require_active_project(project)

        await self.repository.delete(task)
        await self.session.commit()
