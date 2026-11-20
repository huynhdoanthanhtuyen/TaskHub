
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.label import Label
from app.repositories.base import BaseRepository


class LabelRepository(BaseRepository[Label]):
    def __init__(self, session: AsyncSession):
        super().__init__(Label, session)

    async def get_by_project(
        self,
        project_id: UUID,
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[list[Label], int]:
        condition = Label.project_id == project_id

        total = await self.session.scalar(
            select(func.count())
            .select_from(Label)
            .where(condition)
        ) or 0

        result = await self.session.execute(
            select(Label)
            .where(condition)
            .order_by(Label.name, Label.id)
            .offset(offset)
            .limit(limit)
        )

        return list(result.scalars().all()), total
