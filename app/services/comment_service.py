from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import COMMENT_MANAGE_ROLES
from app.core.enums import WorkspaceRole
from app.core.exceptions import (
    CommentDeleteForbiddenError,
    CommentEditForbiddenError,
    CommentNotFoundError,
    ProjectNotFoundError,
    TaskNotFoundError,
    WorkspaceNotFoundError,
)
from app.models.comment import Comment
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.comment_repository import CommentRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.workspace_member_repository import (
    WorkspaceMemberRepository,
)
from app.schemas.comment import CommentCreate, CommentUpdate
from app.services.workspace_access import require_access


class CommentService:
    def __init__(
        self,
        repository: CommentRepository,
        task_repository: TaskRepository,
        member_repository: WorkspaceMemberRepository,
        session: AsyncSession,
    ):
        self.repository = repository
        self.task_repository = task_repository
        self.member_repository = member_repository
        self.session = session

    async def _get_comment(
        self,
        comment_id: UUID,
    ) -> Comment:
        comment = await self.repository.get_by_id(
            comment_id
        )

        if comment is None:
            raise CommentNotFoundError()

        return comment

    async def _get_task(
        self,
        task_id: UUID,
    ) -> Task:
        task = await self.task_repository.get_by_id(task_id)

        if task is None:
            raise TaskNotFoundError()

        return task

    async def _get_project(
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

    async def _get_task_workspace(
        self,
        task: Task,
    ) -> Workspace:
        project = await self._get_project(
            task.project_id
        )

        return await self._get_workspace(
            project.workspace_id
        )

    async def create_comment(
        self,
        task_id: UUID,
        data: CommentCreate,
        current_user: User,
    ) -> Comment:
        task = await self._get_task(task_id)

        workspace = await self._get_task_workspace(task)

        await require_access(
            workspace,
            current_user,
            self.member_repository,
            allowed_roles=COMMENT_MANAGE_ROLES,
            not_found_exc=TaskNotFoundError,
        )

        comment = Comment(
            task_id=task_id,
            author_id=current_user.id,
            content=data.content,
        )

        try:
            self.session.add(comment)
            await self.session.commit()
            await self.session.refresh(comment)

            return comment

        except Exception:
            await self.session.rollback()
            raise

    async def list_comments(
        self,
        task_id: UUID,
        current_user: User,
        offset: int,
        limit: int,
        search: str | None = None,
        author_id: UUID | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> tuple[list[Comment], int]:
        task = await self._get_task(task_id)

        workspace = await self._get_task_workspace(task)

        await require_access(
            workspace,
            current_user,
            self.member_repository,
            not_found_exc=TaskNotFoundError,
        )

        return await self.repository.get_by_task(
            task_id=task_id,
            offset=offset,
            limit=limit,
            search=search,
            author_id=author_id,
            created_from=created_from,
            created_to=created_to,
        )

    async def update_comment(
        self,
        comment_id: UUID,
        data: CommentUpdate,
        current_user: User,
    ) -> Comment:
        comment = await self._get_comment(comment_id)

        task = await self._get_task(comment.task_id)

        workspace = await self._get_task_workspace(task)

        await require_access(
            workspace,
            current_user,
            self.member_repository,
            allowed_roles=COMMENT_MANAGE_ROLES,
            not_found_exc=CommentNotFoundError,
        )

        if comment.author_id != current_user.id:
            raise CommentEditForbiddenError()

        comment.content = data.content

        try:
            await self.session.commit()
            await self.session.refresh(comment)

            return comment

        except Exception:
            await self.session.rollback()
            raise

    async def delete_comment(
        self,
        comment_id: UUID,
        current_user: User,
    ) -> None:
        comment = await self._get_comment(comment_id)

        task = await self._get_task(comment.task_id)

        workspace = await self._get_task_workspace(task)

        await require_access(
            workspace,
            current_user,
            self.member_repository,
            allowed_roles=COMMENT_MANAGE_ROLES,
            not_found_exc=CommentNotFoundError,
        )

        is_author = comment.author_id == current_user.id

        if not is_author:
            is_owner = workspace.owner_id == current_user.id

            if not is_owner:
                member = await self.member_repository.get_member(
                    workspace.id,
                    current_user.id,
                )

                is_owner = (
                    member is not None
                    and member.role == WorkspaceRole.OWNER
                )

            if not is_owner:
                raise CommentDeleteForbiddenError()

        try:
            await self.session.delete(comment)
            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise