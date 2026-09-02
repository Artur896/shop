from functools import lru_cache

from redis.asyncio import Redis, from_url

from app.core.config import settings


@lru_cache
def get_redis() -> Redis:
    return from_url(settings.REDIS_URL, decode_responses=True)
