import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.repositories.base import BaseRepository


class WorkspaceRepository(BaseRepository[Workspace]):
    def __init__(self, session: AsyncSession):
        super().__init__(Workspace, session)

    async def get_by_user(
        self,
        user_id: uuid.UUID,
    ) -> list[Workspace]:
        member_exists = (
            select(WorkspaceMember.workspace_id)
            .where(
                WorkspaceMember.workspace_id == Workspace.id,
                WorkspaceMember.user_id == user_id,
            )
            .exists()
        )

        stmt = (
            select(Workspace)
            .where(
                or_(
                    Workspace.owner_id == user_id,
                    member_exists,
                )
            )
            .order_by(
                Workspace.created_at.desc(),
                Workspace.id.desc(),
            )
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id_for_update(
        self,
        workspace_id: uuid.UUID,
    ) -> Workspace | None:
        stmt = select(Workspace).where(Workspace.id == workspace_id).with_for_update()

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
