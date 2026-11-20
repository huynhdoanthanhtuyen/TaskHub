
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    LabelAlreadyAttachedError,
    LabelAttachConflictError,
    LabelNotAttachedError,
    LabelNotFoundError,
    LabelProjectMismatchError,
)
from app.models.label import Label
from app.repositories.label_repository import LabelRepository
from app.repositories.task_label_repository import TaskLabelRepository
from app.schemas.label import LabelCreate, LabelUpdate
from app.services.workspace_access import WorkspaceAccess


class LabelService:
    def __init__(
        self,
        repository: LabelRepository,
        task_label_repository: TaskLabelRepository,
        session: AsyncSession,
    ):
        self.repository = repository
        self.task_label_repository = task_label_repository
        self.session = session
        self.access = WorkspaceAccess(session)

    async def _get_label(
        self,
        label_id: UUID,
    ) -> Label:
        label = await self.repository.get_by_id(label_id)

        if label is None:
            raise LabelNotFoundError()

        return label

    async def create_label(
        self,
        project_id: UUID,
        data: LabelCreate,
        current_user_id: UUID,
    ) -> Label:
        workspace = await self.access.project_workspace(
            project_id
        )

        await self.access.require_access(
            workspace,
            current_user_id,
            manage=True,
        )

        label = Label(
            project_id=project_id,
            **data.model_dump(),
        )

        try:
            self.session.add(label)
            await self.session.commit()
            await self.session.refresh(label)
            return label

        except Exception:
            await self.session.rollback()
            raise

    async def list_labels(
        self,
        project_id: UUID,
        current_user_id: UUID,
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[list[Label], int]:
        workspace = await self.access.project_workspace(
            project_id
        )

        await self.access.require_access(
            workspace,
            current_user_id,
        )

        return await self.repository.get_by_project(
            project_id,
            offset,
            limit,
        )

    async def update_label(
        self,
        label_id: UUID,
        data: LabelUpdate,
        current_user_id: UUID,
    ) -> Label:
        label = await self._get_label(label_id)

        workspace = await self.access.project_workspace(
            label.project_id
        )

        await self.access.require_access(
            workspace,
            current_user_id,
            manage=True,
        )

        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(label, field, value)

        try:
            await self.session.commit()
            await self.session.refresh(label)
            return label

        except Exception:
            await self.session.rollback()
            raise

    async def delete_label(
        self,
        label_id: UUID,
        current_user_id: UUID,
    ) -> None:
        label = await self._get_label(label_id)

        workspace = await self.access.project_workspace(
            label.project_id
        )

        await self.access.require_access(
            workspace,
            current_user_id,
            manage=True,
        )

        try:
            await self.session.delete(label)
            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise

    async def attach_label(
        self,
        task_id: UUID,
        label_id: UUID,
        current_user_id: UUID,
    ) -> None:
        task = await self.access.get_task(task_id)

        workspace = await self.access.task_workspace(task)

        await self.access.require_access(
            workspace,
            current_user_id,
            manage=True,
        )

        label = await self._get_label(label_id)

        if task.project_id != label.project_id:
            raise LabelProjectMismatchError()

        existing = await self.task_label_repository.get_by_ids(
            task_id,
            label_id,
        )

        if existing is not None:
            raise LabelAlreadyAttachedError()

        try:
            await self.task_label_repository.create(
                task_id,
                label_id,
            )

            await self.session.commit()

        except IntegrityError as exc:
            await self.session.rollback()

            raise LabelAttachConflictError() from exc

        except Exception:
            await self.session.rollback()
            raise

    async def detach_label(
        self,
        task_id: UUID,
        label_id: UUID,
        current_user_id: UUID,
    ) -> None:
        task = await self.access.get_task(task_id)

        workspace = await self.access.task_workspace(task)

        await self.access.require_access(
            workspace,
            current_user_id,
            manage=True,
        )

        label = await self._get_label(label_id)

        if task.project_id != label.project_id:
            raise LabelProjectMismatchError()

        task_label = await self.task_label_repository.get_by_ids(
            task_id,
            label_id,
        )

        if task_label is None:
            raise LabelNotAttachedError()

        try:
            await self.task_label_repository.delete(
                task_label
            )

            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise
