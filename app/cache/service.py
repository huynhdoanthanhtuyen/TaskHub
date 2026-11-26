import logging
from typing import Any

from pydantic import BaseModel, ValidationError
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self, client: Redis | None) -> None:
        self._client = client

    @property
    def enabled(self) -> bool:
        return (
            settings.CACHE_ENABLED
            and self._client is not None
        )

    async def get[T: BaseModel](
        self,
        key: str,
        response_model: type[T],
    ) -> T | None:
        if not self.enabled or self._client is None:
            return None

        try:
            cached_data = await self._client.get(key)

            if cached_data is None:
                logger.debug("Cache MISS: %s", key)
                return None

            result = response_model.model_validate_json(
                cached_data,
            )

            logger.debug("Cache HIT: %s", key)

            return result

        except ValidationError:
            logger.warning(
                "Invalid cached data: %s",
                key,
                exc_info=True,
            )

            await self.delete(key)
            return None

        except RedisError:
            logger.warning(
                "Failed to read cache: %s",
                key,
                exc_info=True,
            )

            return None

    async def set(
        self,
        key: str,
        value: BaseModel,
        ttl: int | None = None,
    ) -> bool:
        if not self.enabled or self._client is None:
            return False

        expiration = (
            settings.CACHE_TTL_SECONDS
            if ttl is None
            else ttl
        )

        if expiration <= 0:
            raise ValueError("Cache TTL must be positive")

        try:
            result = await self._client.set(
                key,
                value.model_dump_json(),
                ex=expiration,
            )

            logger.debug(
                "Cache SET: %s (TTL=%s)",
                key,
                expiration,
            )

            return bool(result)

        except RedisError:
            logger.warning(
                "Failed to write cache: %s",
                key,
                exc_info=True,
            )

            return False

    async def delete(self, key: str) -> bool:
        if not self.enabled or self._client is None:
            return False

        try:
            await self._client.delete(key)

            logger.debug("Cache DELETE: %s", key)

            return True

        except RedisError:
            logger.warning(
                "Failed to delete cache: %s",
                key,
                exc_info=True,
            )

            return False

    async def invalidate(self, pattern: str) -> int:
        if not self.enabled or self._client is None:
            return 0

        deleted_count = 0
        keys: list[Any] = []

        try:
            async for key in self._client.scan_iter(
                match=pattern,
                count=100,
            ):
                keys.append(key)

                if len(keys) >= 100:
                    deleted_count += await self._client.delete(
                        *keys,
                    )
                    keys.clear()

            if keys:
                deleted_count += await self._client.delete(
                    *keys,
                )

            logger.debug(
                "Cache INVALIDATE: %s (%s keys)",
                pattern,
                deleted_count,
            )

        except RedisError:
            logger.warning(
                "Failed to invalidate cache: %s",
                pattern,
                exc_info=True,
            )

        return deleted_count