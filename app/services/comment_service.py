
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import WorkspaceRole
from app.core.exceptions import (
    CommentDeleteForbiddenError,
    CommentEditForbiddenError,
    CommentNotFoundError,
)
from app.models.comment import Comment
from app.repositories.comment_repository import CommentRepository
from app.schemas.comment import CommentCreate, CommentUpdate
from app.services.workspace_access import WorkspaceAccess


class CommentService:
    def __init__(
        self,
        repository: CommentRepository,
        session: AsyncSession,
    ):
        self.repository = repository
        self.session = session
        self.access = WorkspaceAccess(session)

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

    async def create_comment(
        self,
        task_id: UUID,
        data: CommentCreate,
        current_user_id: UUID,
    ) -> Comment:
        task = await self.access.get_task(task_id)

        workspace = await self.access.task_workspace(
            task
        )

        await self.access.require_access(
            workspace,
            current_user_id,
            manage=True,
        )

        comment = Comment(
            task_id=task_id,
            author_id=current_user_id,
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
        current_user_id: UUID,
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[list[Comment], int]:
        task = await self.access.get_task(task_id)

        workspace = await self.access.task_workspace(
            task
        )

        await self.access.require_access(
            workspace,
            current_user_id,
        )

        return await self.repository.get_by_task(
            task_id,
            offset,
            limit,
        )

    async def update_comment(
        self,
        comment_id: UUID,
        data: CommentUpdate,
        current_user_id: UUID,
    ) -> Comment:
        comment = await self._get_comment(comment_id)

        task = await self.access.get_task(
            comment.task_id
        )

        workspace = await self.access.task_workspace(
            task
        )

        await self.access.require_access(
            workspace,
            current_user_id,
            manage=True,
        )

        if comment.author_id != current_user_id:
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
        current_user_id: UUID,
    ) -> None:
        comment = await self._get_comment(comment_id)

        task = await self.access.get_task(
            comment.task_id
        )

        workspace = await self.access.task_workspace(
            task
        )

        role = await self.access.require_access(
            workspace,
            current_user_id,
            manage=True,
        )

        is_author = comment.author_id == current_user_id
        is_owner = role == WorkspaceRole.OWNER

        if not is_author and not is_owner:
            raise CommentDeleteForbiddenError()

        try:
            await self.session.delete(comment)
            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise
