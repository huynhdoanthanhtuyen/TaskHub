
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task_label import TaskLabel


class TaskLabelRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_ids(
        self,
        task_id: UUID,
        label_id: UUID,
    ) -> TaskLabel | None:
        result = await self.session.execute(
            select(TaskLabel).where(
                TaskLabel.task_id == task_id,
                TaskLabel.label_id == label_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        task_id: UUID,
        label_id: UUID,
    ) -> TaskLabel:
        task_label = TaskLabel(
            task_id=task_id,
            label_id=label_id,
        )
        self.session.add(task_label)
        return task_label

    async def delete(self, task_label: TaskLabel) -> None:
        await self.session.delete(task_label)
