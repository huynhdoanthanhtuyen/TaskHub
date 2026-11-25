from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.repositories.base import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    def __init__(self, session: AsyncSession):
        super().__init__(Comment, session)

    async def get_by_task(
        self,
        task_id: UUID,
        offset: int,
        limit: int,
    ) -> tuple[list[Comment], int]:
        condition = Comment.task_id == task_id

        total = await self.session.scalar(
            select(func.count())
            .select_from(Comment)
            .where(condition)
        ) or 0

        result = await self.session.execute(
            select(Comment)
            .where(condition)
            .order_by(
                Comment.created_at.asc(),
                Comment.id.asc(),
            )
            .offset(offset)
            .limit(limit)
        )

        return list(result.scalars().all()), total