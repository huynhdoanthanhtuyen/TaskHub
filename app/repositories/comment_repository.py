from datetime import datetime
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
        search: str | None = None,
        author_id: UUID | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> tuple[list[Comment], int]:
        conditions = [Comment.task_id == task_id]

        if search:
            conditions.append(
                Comment.content.icontains(
                    search,
                    autoescape=True,
                )
            )

        if author_id is not None:
            conditions.append(Comment.author_id == author_id)

        if created_from is not None:
            conditions.append(Comment.created_at >= created_from)

        if created_to is not None:
            conditions.append(Comment.created_at <= created_to)

        count_stmt = select(func.count()).select_from(Comment).where(*conditions)

        total = await self.session.scalar(count_stmt) or 0

        stmt = (
            select(Comment)
            .where(*conditions)
            .order_by(
                Comment.created_at.asc(),
                Comment.id.asc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all()), total
