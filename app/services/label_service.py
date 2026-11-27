from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import LABEL_MANAGE_ROLES
from app.core.exceptions import (
    LabelAlreadyAttachedError,
    LabelNameAlreadyExistsError,
    LabelNotAttachedError,
    LabelNotFoundError,
    LabelProjectMismatchError,
    ProjectNotFoundError,
    TaskNotFoundError,
    WorkspaceNotFoundError,
)
from app.models.label import Label
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.label_repository import LabelRepository
from app.repositories.task_label_repository import TaskLabelRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.workspace_member_repository import (
    WorkspaceMemberRepository,
)
from app.schemas.label import LabelCreate, LabelUpdate
from app.services.workspace_access import require_access


def _is_duplicate_label_name(exc: IntegrityError) -> bool:
    original = exc.orig
    cause = getattr(original, "__cause__", None)

    for error in (original, cause):
        if error is None:
            continue

        constraint_name = getattr(
            error,
            "constraint_name",
            None,
        )

        if constraint_name == "uq_labels_project_id_name":
            return True

    return False


class LabelService:
    def __init__(
        self,
        repository: LabelRepository,
        task_label_repository: TaskLabelRepository,
        task_repository: TaskRepository,
        member_repository: WorkspaceMemberRepository,
        session: AsyncSession,
    ):
        self.repository = repository
        self.task_label_repository = task_label_repository
        self.task_repository = task_repository
        self.member_repository = member_repository
        self.session = session

    async def _get_label(
        self,
        label_id: UUID,
    ) -> Label:
        label = await self.repository.get_by_id(label_id)

        if label is None:
            raise LabelNotFoundError()

        return label

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

    async def _get_task(
        self,
        task_id: UUID,
    ) -> Task:
        task = await self.task_repository.get_by_id(task_id)

        if task is None:
            raise TaskNotFoundError()

        return task

    async def _get_project_workspace(
        self,
        project_id: UUID,
    ) -> Workspace:
        project = await self._get_project(project_id)

        return await self._get_workspace(project.workspace_id)

    async def create_label(
        self,
        project_id: UUID,
        data: LabelCreate,
        current_user: User,
    ) -> Label:
        workspace = await self._get_project_workspace(project_id)

        await require_access(
            workspace,
            current_user,
            self.member_repository,
            allowed_roles=LABEL_MANAGE_ROLES,
            not_found_exc=ProjectNotFoundError,
        )

        label = Label(
            project_id=project_id,
            **data.model_dump(),
        )

        try:
            self.session.add(label)
            await self.session.commit()

        except IntegrityError as exc:
            await self.session.rollback()

            if _is_duplicate_label_name(exc):
                raise LabelNameAlreadyExistsError() from exc

            raise

        await self.session.refresh(label)

        return label

    async def list_labels(
        self,
        project_id: UUID,
        current_user: User,
        offset: int,
        limit: int,
        search: str | None = None,
        color: str | None = None,
    ) -> tuple[list[Label], int]:
        workspace = await self._get_project_workspace(project_id)

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
            search=search,
            color=color,
        )

    async def list_labels_by_task(
        self,
        task_id: UUID,
        current_user: User,
        offset: int,
        limit: int,
        search: str | None = None,
        color: str | None = None,
    ) -> tuple[list[Label], int]:
        task = await self._get_task(task_id)

        workspace = await self._get_project_workspace(task.project_id)

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
            color=color,
        )

    async def update_label(
        self,
        label_id: UUID,
        data: LabelUpdate,
        current_user: User,
    ) -> Label:
        label = await self._get_label(label_id)

        workspace = await self._get_project_workspace(label.project_id)

        await require_access(
            workspace,
            current_user,
            self.member_repository,
            allowed_roles=LABEL_MANAGE_ROLES,
            not_found_exc=LabelNotFoundError,
        )

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(label, field, value)

        try:
            await self.session.commit()

        except IntegrityError as exc:
            await self.session.rollback()

            if _is_duplicate_label_name(exc):
                raise LabelNameAlreadyExistsError() from exc

            raise

        await self.session.refresh(label)

        return label

    async def delete_label(
        self,
        label_id: UUID,
        current_user: User,
    ) -> None:
        label = await self._get_label(label_id)

        workspace = await self._get_project_workspace(label.project_id)

        await require_access(
            workspace,
            current_user,
            self.member_repository,
            allowed_roles=LABEL_MANAGE_ROLES,
            not_found_exc=LabelNotFoundError,
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
        current_user: User,
    ) -> None:
        task = await self._get_task(task_id)

        workspace = await self._get_project_workspace(task.project_id)

        await require_access(
            workspace,
            current_user,
            self.member_repository,
            allowed_roles=LABEL_MANAGE_ROLES,
            not_found_exc=TaskNotFoundError,
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

            sqlstate = getattr(
                exc.orig,
                "sqlstate",
                None,
            )

            if sqlstate == "23505":
                raise LabelAlreadyAttachedError() from exc

            raise

        except Exception:
            await self.session.rollback()
            raise

    async def detach_label(
        self,
        task_id: UUID,
        label_id: UUID,
        current_user: User,
    ) -> None:
        task = await self._get_task(task_id)

        workspace = await self._get_project_workspace(task.project_id)

        await require_access(
            workspace,
            current_user,
            self.member_repository,
            allowed_roles=LABEL_MANAGE_ROLES,
            not_found_exc=TaskNotFoundError,
        )

        task_label = await self.task_label_repository.get_by_ids(
            task_id,
            label_id,
        )

        if task_label is None:
            raise LabelNotAttachedError()

        try:
            await self.task_label_repository.delete(task_label)

            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise
