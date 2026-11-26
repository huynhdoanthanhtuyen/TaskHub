import asyncio

from pydantic import BaseModel

from app.cache.keys import CacheKey
from app.cache.service import CacheService
from app.db.redis import create_redis_client


class TestResponse(BaseModel):
    name: str
    total: int


async def main() -> None:
    client = create_redis_client()
    cache = CacheService(client)

    key = CacheKey.build(
        resource="test",
        scope="manual",
        operation="list",
        offset=0,
        limit=10,
    )

    try:
        await cache.delete(key)

        # Test Cache MISS
        result = await cache.get(key, TestResponse)
        print("Cache MISS:", result)
        assert result is None

        # Test Cache SET
        data = TestResponse(
            name="TaskHub",
            total=10,
        )

        saved = await cache.set(key, data, ttl=60)
        print("Cache SET:", saved)
        assert saved

        # Test Cache HIT
        result = await cache.get(key, TestResponse)
        print("Cache HIT:", result)
        assert result == data

        # Test TTL
        ttl = await client.ttl(key)
        print("TTL:", ttl)
        assert 0 < ttl <= 60

        # Test Cache Invalidation
        pattern = CacheKey.pattern(
            resource="test",
            scope="manual",
        )

        deleted = await cache.invalidate(pattern)
        print("Invalidated:", deleted)
        assert deleted >= 1

        # Test after invalidation
        result = await cache.get(key, TestResponse)
        print("After invalidation:", result)
        assert result is None

        print("All cache tests passed!")

    finally:
        await cache.delete(key)
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())