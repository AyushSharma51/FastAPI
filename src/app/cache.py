import redis.asyncio as aioredis
import json
from .config import REDIS_HOST, REDIS_PORT, REDIS_DB, CACHE_TTL
import hashlib


def make_cache_key(prefix: str, **kwargs) -> str:
    """
    Generates a consistent, safe cache key from any params.
    
    Usage:
        make_cache_key("matches", status="active", page=1, limit=10)
        → "matches:a3f5c1d2e4b6..."
    """
    # Sort keys so order doesn't matter
    # e.g. (status=active, page=1) == (page=1, status=active)
    normalized = json.dumps(kwargs, sort_keys=True, default=str)
    
    hash_part = hashlib.md5(normalized.encode()).hexdigest()[:12]
    
    return f"{prefix}:{hash_part}"

# Module-level client (initialized at startup)
redis_client: aioredis.Redis | None = None

async def init_redis():
    """Call this at startup to create and validate the Redis connection."""
    global redis_client
    redis_client = aioredis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True
    )
    await redis_client.ping()  # Fail fast if Redis is unreachable 
    print("Redis connected successfully")

async def close_redis():
    """Call this at shutdown to cleanly close the connection."""
    if redis_client:
        await redis_client.aclose()

async def get_cache(key: str):
    data = await redis_client.get(key)
    return json.loads(data) if data else None

async def set_cache(key: str, value: dict, ttl: int = CACHE_TTL):
    await redis_client.setex(key, ttl, json.dumps(value))

async def delete_cache(key: str):
    await redis_client.delete(key)

async def delete_cache_pattern(pattern: str):
    """Delete all keys matching a pattern e.g. 'matches:*'"""
    keys = await redis_client.keys(pattern)
    if keys:
        await redis_client.delete(*keys)