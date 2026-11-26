from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.label import Label
from app.models.task_label import TaskLabel
from app.repositories.base import BaseRepository


class LabelRepository(BaseRepository[Label]):
    def __init__(self, session: AsyncSession):
        super().__init__(Label, session)

    async def get_by_task(
        self,
        task_id: UUID,
        offset: int,
        limit: int,
        search: str | None = None,
        color: str | None = None,
    ) -> tuple[list[Label], int]:
        conditions = [
            TaskLabel.task_id == task_id
        ]

        if search:
            conditions.append(
                Label.name.icontains(
                    search,
                    autoescape=True,
                )
            )

        if color is not None:
            conditions.append(
                func.lower(Label.color) == color.lower()
            )

        count_stmt = (
            select(func.count())
            .select_from(Label)
            .join(
                TaskLabel,
                TaskLabel.label_id == Label.id,
            )
            .where(*conditions)
        )

        total = await self.session.scalar(count_stmt) or 0

        stmt = (
            select(Label)
            .join(
                TaskLabel,
                TaskLabel.label_id == Label.id,
            )
            .where(*conditions)
            .order_by(
                Label.name.asc(),
                Label.id.asc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all()), total

    async def get_by_project(
        self,
        project_id: UUID,
        offset: int,
        limit: int,
        search: str | None = None,
        color: str | None = None,
    ) -> tuple[list[Label], int]:
        conditions = [
            Label.project_id == project_id
        ]

        if search:
            conditions.append(
                Label.name.icontains(
                    search,
                    autoescape=True,
                )
            )

        if color is not None:
            conditions.append(
                func.lower(Label.color) == color.lower()
            )

        count_stmt = (
            select(func.count())
            .select_from(Label)
            .where(*conditions)
        )

        total = await self.session.scalar(count_stmt) or 0

        stmt = (
            select(Label)
            .where(*conditions)
            .order_by(
                Label.name.asc(),
                Label.id.asc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all()), total