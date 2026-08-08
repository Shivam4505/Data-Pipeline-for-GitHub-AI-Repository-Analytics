# GitHub AI Repository Analytics - API Cache Layer
import json
from typing import Any, Optional
import redis.asyncio as redis
import structlog

from .config import settings

logger = structlog.get_logger(__name__)


class CacheManager:
    """Manages Redis caching for the API."""

    def __init__(self):
        self._client: Optional[redis.Redis] = None

    async def initialize(self) -> None:
        """Initialize Redis connection."""
        self._client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        logger.info("cache_initialized")

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
        logger.info("cache_closed")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not settings.cache_enabled or not self._client:
            return None
        try:
            value = await self._client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.warning("cache_get_failed", key=key, error=str(e))
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        if not settings.cache_enabled or not self._client:
            return False
        try:
            ttl = ttl or settings.cache_ttl_seconds
            await self._client.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception as e:
            logger.warning("cache_set_failed", key=key, error=str(e))
        return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self._client:
            return False
        try:
            await self._client.delete(key)
            return True
        except Exception as e:
            logger.warning("cache_delete_failed", key=key, error=str(e))
        return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self._client:
            return 0
        try:
            keys = []
            async for key in self._client.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                return await self._client.delete(*keys)
        except Exception as e:
            logger.warning("cache_delete_pattern_failed", pattern=pattern, error=str(e))
        return 0

    def make_key(self, prefix: str, *parts: str) -> str:
        """Create a cache key."""
        return f"github_analytics:{prefix}:{':'.join(parts)}"


# Global cache manager instance
cache_manager = CacheManager()


async def get_cache() -> CacheManager:
    """FastAPI dependency for cache manager."""
    return cache_manager