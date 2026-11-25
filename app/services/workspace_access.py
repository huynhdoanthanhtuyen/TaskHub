from app.core.enums import WorkspaceRole
from app.core.exceptions import (
    AppException,
    PermissionDeniedError,
    WorkspaceNotFoundError,
)
from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.workspace_member_repository import (
    WorkspaceMemberRepository,
)


async def require_access(
    workspace: Workspace,
    current_user: User,
    member_repository: WorkspaceMemberRepository,
    *,
    allowed_roles: frozenset[WorkspaceRole] | None = None,
    not_found_exc: type[AppException] = WorkspaceNotFoundError,
) -> None:
    if workspace.owner_id == current_user.id:
        return

    member = await member_repository.get_member(
        workspace.id,
        current_user.id,
    )

    if member is None:
        raise not_found_exc()

    if allowed_roles is not None and member.role not in allowed_roles:
        raise PermissionDeniedError()