import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.keys import CacheKey
from app.cache.service import CacheService
from app.core.enums import WorkspaceRole
from app.core.exceptions import (
    WorkspaceHasProjectsError,
    WorkspaceInvalidRoleError,
    WorkspaceMemberAlreadyExistsError,
    WorkspaceMemberNotFoundError,
    WorkspaceMemberUserNotFoundError,
    WorkspaceNotFoundError,
    WorkspaceOwnerCannotBeInvitedError,
    WorkspaceOwnerCannotBeRemovedError,
    WorkspaceOwnerRequiredError,
)
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_member_repository import (
    WorkspaceMemberRepository,
)
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceListResponse,
    WorkspaceMemberCreate,
    WorkspaceResponse,
    WorkspaceUpdate,
)
from app.services.workspace_access import require_access


class WorkspaceService:
    def __init__(
        self,
        workspace_repository: WorkspaceRepository,
        member_repository: WorkspaceMemberRepository,
        user_repository: UserRepository,
        session: AsyncSession,
        cache: CacheService,
    ):
        self.workspace_repository = workspace_repository
        self.member_repository = member_repository
        self.user_repository = user_repository
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

    def _require_owner(
        self,
        workspace: Workspace,
        current_user: User,
    ) -> None:
        if workspace.owner_id != current_user.id:
            raise WorkspaceOwnerRequiredError()

    async def _invalidate_workspace_cache(
        self,
        user_id: uuid.UUID | None = None,
    ) -> None:
        pattern = CacheKey.pattern(
            resource="workspaces",
            scope=user_id if user_id is not None else "*",
            operation="list",
        )

        await self.cache.invalidate(pattern)

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
        await self.session.flush()

        owner_member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=current_user.id,
            role=WorkspaceRole.OWNER,
        )

        self.session.add(owner_member)

        await self.session.commit()

        await self._invalidate_workspace_cache(
            current_user.id,
        )

        await self.session.refresh(workspace)

        return workspace

    async def list_workspaces(
        self,
        offset: int,
        limit: int,
        current_user: User,
        role: WorkspaceRole | None = None,
        search: str | None = None,
    ) -> WorkspaceListResponse:
        cache_key = CacheKey.build(
            resource="workspaces",
            scope=current_user.id,
            operation="list",
            offset=offset,
            limit=limit,
            role=role,
            search=search,
        )

        cached_response = await self.cache.get(
            cache_key,
            WorkspaceListResponse,
        )

        if cached_response is not None:
            workspace_ids = [workspace.id for workspace in cached_response.items]

            has_access = await self.workspace_repository.can_access_all(
                user_id=current_user.id,
                workspace_ids=workspace_ids,
                role=role,
            )

            if has_access:
                return cached_response

            await self.cache.delete(cache_key)

        workspaces, total = await self.workspace_repository.get_by_user(
            offset=offset,
            limit=limit,
            user_id=current_user.id,
            role=role,
            search=search,
        )

        response = WorkspaceListResponse(
            items=[
                WorkspaceResponse.model_validate(workspace) for workspace in workspaces
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

    async def get_workspace(
        self,
        workspace_id: uuid.UUID,
        current_user: User,
    ) -> Workspace:
        workspace = await self._get_workspace(workspace_id)

        await require_access(
            workspace,
            current_user,
            self.member_repository,
        )

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

        await self._invalidate_workspace_cache()

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
            raise WorkspaceHasProjectsError()

        await self._invalidate_workspace_cache()

    async def add_member(
        self,
        workspace_id: uuid.UUID,
        data: WorkspaceMemberCreate,
        current_user: User,
    ) -> WorkspaceMember:
        workspace = await self.workspace_repository.get_by_id(
            workspace_id,
        )

        if workspace is None:
            raise WorkspaceNotFoundError()

        self._require_owner(workspace, current_user)

        if data.user_id == workspace.owner_id:
            raise WorkspaceOwnerCannotBeInvitedError()

        if data.role == WorkspaceRole.OWNER:
            raise WorkspaceInvalidRoleError()

        user = await self.user_repository.get_by_id(
            data.user_id,
        )

        if user is None:
            raise WorkspaceMemberUserNotFoundError()

        existing_member = await self.member_repository.get_member(
            workspace_id,
            data.user_id,
        )

        if existing_member is not None:
            raise WorkspaceMemberAlreadyExistsError()

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
            raise WorkspaceMemberAlreadyExistsError()

        await self._invalidate_workspace_cache(
            data.user_id,
        )

        await self.session.refresh(member)

        return member

    async def list_members(
        self,
        workspace_id: uuid.UUID,
        current_user: User,
    ) -> list[WorkspaceMember]:
        workspace = await self._get_workspace(workspace_id)

        await require_access(
            workspace,
            current_user,
            self.member_repository,
        )

        return await self.member_repository.get_members(
            workspace_id,
        )

    async def remove_member(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        current_user: User,
    ) -> None:
        workspace = await self.workspace_repository.get_by_id(
            workspace_id,
        )

        if workspace is None:
            raise WorkspaceNotFoundError()

        self._require_owner(workspace, current_user)

        if user_id == workspace.owner_id:
            raise WorkspaceOwnerCannotBeRemovedError()

        member = await self.member_repository.get_member(
            workspace_id,
            user_id,
        )

        if member is None:
            raise WorkspaceMemberNotFoundError()

        await self.member_repository.delete(member)

        await self.session.commit()

        await self._invalidate_workspace_cache(user_id)
