import logging

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import settings

logger = logging.getLogger(__name__)


def create_redis_client() -> Redis:
    return Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=settings.REDIS_TIMEOUT_SECONDS,
        socket_timeout=settings.REDIS_TIMEOUT_SECONDS,
    )


async def check_redis_connection(client: Redis) -> bool:
    try:
        await client.ping()

        logger.info("Redis connection established")

        return True

    except RedisError:
        logger.warning(
            "Redis is unavailable. Falling back to PostgreSQL.",
            exc_info=True,
        )

        return False


async def close_redis_connection(client: Redis) -> None:
    await client.aclose()

    logger.info("Redis connection closed")
