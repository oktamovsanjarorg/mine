import json
import structlog
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional
import redis.asyncio as redis
from redis.asyncio.client import Redis
from redis.exceptions import LockError

from src.config import settings

logger = structlog.get_logger()

redis_client: Optional[Redis] = None

async def create_redis_pool() -> None:
    """Create a Redis connection pool."""
    global redis_client
    redis_client = redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=settings.redis_max_connections,
    )
    logger.info("Redis connection established")

async def close_redis() -> None:
    """Close the Redis connection pool."""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")

async def cache_get(key: str) -> Optional[Any]:
    """Get a value from cache."""
    if not redis_client:
        raise RuntimeError("Redis not initialized")
    value = await redis_client.get(key)
    if value:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return None

async def cache_set(key: str, value: Any, ttl: int = 3600) -> None:
    """Set a value in cache with a TTL."""
    if not redis_client:
        raise RuntimeError("Redis not initialized")
    if isinstance(value, (dict, list)):
        value = json.dumps(value)
    await redis_client.set(key, value, ex=ttl)

async def cache_delete(key: str) -> None:
    """Delete a value from cache."""
    if not redis_client:
        raise RuntimeError("Redis not initialized")
    await redis_client.delete(key)

async def cache_delete_pattern(pattern: str) -> None:
    """Delete multiple values from cache using a pattern."""
    if not redis_client:
        raise RuntimeError("Redis not initialized")
    keys = await redis_client.keys(pattern)
    if keys:
        await redis_client.delete(*keys)

async def rate_limit_check(user_id: int, action: str, limit: int, period: int) -> bool:
    """Check if a user has exceeded the rate limit for a specific action."""
    if not redis_client:
        raise RuntimeError("Redis not initialized")
    key = f"rate_limit:{action}:{user_id}"
    current = await redis_client.get(key)
    if current and int(current) >= limit:
        return False
    
    pipeline = redis_client.pipeline()
    pipeline.incr(key)
    if not current:
        pipeline.expire(key, period)
    await pipeline.execute()
    return True

@asynccontextmanager
async def acquire_lock(name: str, timeout: int = 10) -> AsyncGenerator[bool, None]:
    """Acquire a distributed lock using Redis SET NX EX."""
    if not redis_client:
        raise RuntimeError("Redis not initialized")
    lock_key = f"lock:{name}"
    lock = redis_client.lock(lock_key, timeout=timeout)
    try:
        acquired = await lock.acquire(blocking=True, blocking_timeout=timeout)
        if acquired:
            yield True
        else:
            yield False
    finally:
        try:
            await lock.release()
        except LockError:
            pass
