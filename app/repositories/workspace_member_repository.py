import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace_member import WorkspaceMember


class WorkspaceMemberRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_member(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> WorkspaceMember | None:
        stmt = select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_members(
        self,
        workspace_id: uuid.UUID,
    ) -> list[WorkspaceMember]:
        stmt = (
            select(WorkspaceMember)
            .where(WorkspaceMember.workspace_id == workspace_id)
            .order_by(WorkspaceMember.user_id)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    def add(self, member: WorkspaceMember) -> None:
        self.session.add(member)

    async def delete(self, member: WorkspaceMember) -> None:
        await self.session.delete(member)
