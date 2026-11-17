import uuid

from fastapi import status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import messages
from app.core.enums import WorkspaceRole
from app.core.exceptions import AppException
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_member_repository import WorkspaceMemberRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceMemberCreate,
    WorkspaceUpdate,
)


class WorkspaceService:
    def __init__(
        self,
        workspace_repository: WorkspaceRepository,
        member_repository: WorkspaceMemberRepository,
        user_repository: UserRepository,
        session: AsyncSession,
    ):
        self.workspace_repository = workspace_repository
        self.member_repository = member_repository
        self.user_repository = user_repository
        self.session = session

    async def _get_workspace(
        self,
        workspace_id: uuid.UUID,
    ) -> Workspace:
        workspace = await self.workspace_repository.get_by_id(workspace_id)

        if workspace is None:
            raise AppException(
                messages.WORKSPACE_NOT_FOUND,
                status.HTTP_404_NOT_FOUND,
            )

        return workspace

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
            raise AppException(
                messages.WORKSPACE_ACCESS_DENIED,
                status.HTTP_403_FORBIDDEN,
            )

    def _require_owner(
        self,
        workspace: Workspace,
        current_user: User,
    ) -> None:
        if workspace.owner_id != current_user.id:
            raise AppException(
                messages.WORKSPACE_OWNER_REQUIRED,
                status.HTTP_403_FORBIDDEN,
            )

    async def create_workspace(
        self,
        data: WorkspaceCreate,
        current_user: User,
    ) -> Workspace:
        workspace = Workspace(
            name=data.name,
            owner_id=current_user.id,
        )

        self.session.add(workspace)
        await self.session.commit()
        await self.session.refresh(workspace)

        return workspace

    async def list_workspaces(
        self,
        current_user: User,
    ) -> list[Workspace]:
        return await self.workspace_repository.get_by_user(current_user.id)

    async def get_workspace(
        self,
        workspace_id: uuid.UUID,
        current_user: User,
    ) -> Workspace:
        workspace = await self._get_workspace(workspace_id)

        await self._require_access(workspace, current_user)

        return workspace

    async def update_workspace(
        self,
        workspace_id: uuid.UUID,
        data: WorkspaceUpdate,
        current_user: User,
    ) -> Workspace:
        workspace = await self._get_workspace(workspace_id)

        self._require_owner(workspace, current_user)

        workspace.name = data.name

        await self.session.commit()
        await self.session.refresh(workspace)

        return workspace

    async def delete_workspace(
        self,
        workspace_id: uuid.UUID,
        current_user: User,
    ) -> None:
        workspace = await self._get_workspace(workspace_id)

        self._require_owner(workspace, current_user)

        try:
            await self.session.delete(workspace)
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise AppException(
                messages.WORKSPACE_HAS_PROJECTS,
                status.HTTP_409_CONFLICT,
            )

    async def add_member(
        self,
        workspace_id: uuid.UUID,
        data: WorkspaceMemberCreate,
        current_user: User,
    ) -> WorkspaceMember:
        workspace = await self.workspace_repository.get_by_id_for_update(workspace_id)

        if workspace is None:
            raise AppException(
                messages.WORKSPACE_NOT_FOUND,
                status.HTTP_404_NOT_FOUND,
            )

        self._require_owner(workspace, current_user)

        if data.user_id == workspace.owner_id:
            raise AppException(
                messages.WORKSPACE_OWNER_CANNOT_BE_INVITED,
                status.HTTP_400_BAD_REQUEST,
            )

        if data.role == WorkspaceRole.OWNER:
            raise AppException(
                messages.WORKSPACE_INVALID_ROLE,
                status.HTTP_400_BAD_REQUEST,
            )

        user = await self.user_repository.get_by_id(data.user_id)

        if user is None:
            raise AppException(
                messages.WORKSPACE_MEMBER_USER_NOT_FOUND,
                status.HTTP_404_NOT_FOUND,
            )

        existing_member = await self.member_repository.get_member(
            workspace_id,
            data.user_id,
        )

        if existing_member is not None:
            raise AppException(
                messages.WORKSPACE_MEMBER_ALREADY_EXISTS,
                status.HTTP_409_CONFLICT,
            )

        member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=data.user_id,
            role=data.role,
        )

        self.member_repository.add(member)

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise AppException(
                messages.WORKSPACE_MEMBER_ALREADY_EXISTS,
                status.HTTP_409_CONFLICT,
            )

        await self.session.refresh(member)
        return member

    async def list_members(
        self,
        workspace_id: uuid.UUID,
        current_user: User,
    ) -> list[WorkspaceMember]:
        workspace = await self._get_workspace(workspace_id)

        await self._require_access(workspace, current_user)

        return await self.member_repository.get_members(workspace_id)

    async def remove_member(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        current_user: User,
    ) -> None:
        workspace = await self.workspace_repository.get_by_id_for_update(workspace_id)

        if workspace is None:
            raise AppException(
                messages.WORKSPACE_NOT_FOUND,
                status.HTTP_404_NOT_FOUND,
            )

        self._require_owner(workspace, current_user)

        if user_id == workspace.owner_id:
            raise AppException(
                messages.WORKSPACE_OWNER_CANNOT_BE_REMOVED,
                status.HTTP_400_BAD_REQUEST,
            )

        member = await self.member_repository.get_member(
            workspace_id,
            user_id,
        )

        if member is None:
            raise AppException(
                messages.WORKSPACE_MEMBER_NOT_FOUND,
                status.HTTP_404_NOT_FOUND,
            )

        await self.member_repository.delete(member)
        await self.session.commit()
