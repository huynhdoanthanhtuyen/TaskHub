import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import WorkspaceRole
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.repositories.base import BaseRepository


class WorkspaceRepository(BaseRepository[Workspace]):
    def __init__(self, session: AsyncSession):
        super().__init__(Workspace, session)

    async def get_by_user(
        self,
        offset: int,
        limit: int,
        user_id: uuid.UUID,
        role: WorkspaceRole | None = None,
        search: str | None = None,
    ) -> tuple[list[Workspace], int]:
        member_exists = (
            select(WorkspaceMember.workspace_id)
            .where(
                WorkspaceMember.workspace_id == Workspace.id,
                WorkspaceMember.user_id == user_id,
            )
            .exists()
        )

        conditions = [
            or_(
                Workspace.owner_id == user_id,
                member_exists,
            )
        ]

        if role == WorkspaceRole.OWNER:
            conditions.append(
                Workspace.owner_id == user_id
            )

        elif role is not None:
            member_with_role_exists = (
                select(WorkspaceMember.workspace_id)
                .where(
                    WorkspaceMember.workspace_id == Workspace.id,
                    WorkspaceMember.user_id == user_id,
                    WorkspaceMember.role == role,
                )
                .exists()
            )

            conditions.append(
                Workspace.owner_id != user_id
            )

            conditions.append(member_with_role_exists)

        if search:
            conditions.append(
                Workspace.name.icontains(
                    search,
                    autoescape=True,
                )
            )

        count_stmt = (
            select(func.count())
            .select_from(Workspace)
            .where(*conditions)
        )

        total = await self.session.scalar(count_stmt) or 0

        stmt = (
            select(Workspace)
            .where(*conditions)
            .order_by(
                Workspace.created_at.desc(),
                Workspace.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all()), total