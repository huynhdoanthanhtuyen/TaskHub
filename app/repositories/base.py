from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase


class BaseRepository[ModelType: DeclarativeBase]:
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 10,
    ) -> list[ModelType]:
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, obj_id: UUID) -> ModelType | None:
        return await self.session.get(self.model, obj_id)

    async def update(
        self,
        obj: ModelType,
        data: dict,
    ) -> ModelType:
        for key, value in data.items():
            setattr(obj, key, value)

        await self.session.flush()
        return obj

    async def delete(self, obj: ModelType) -> None:
        await self.session.delete(obj)
        await self.session.flush()
