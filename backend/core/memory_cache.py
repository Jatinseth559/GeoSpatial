"""
In-memory cache implementation for development without Redis.
"""

import asyncio
import time
from typing import Any, Dict, Optional


class MemoryCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        async with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if entry['expires'] > time.time():
                    return entry['value']
                else:
                    del self._cache[key]
            return None
    
    async def set(self, key: str, value: str, ex: int = 300) -> None:
        """Set value in cache with expiration."""
        async with self._lock:
            self._cache[key] = {
                'value': value,
                'expires': time.time() + ex
            }
    
    async def delete(self, key: str) -> None:
        """Delete key from cache."""
        async with self._lock:
            self._cache.pop(key, None)
    
    async def ping(self) -> bool:
        """Health check."""
        return True
    
    async def flushall(self) -> None:
        """Clear all cache."""
        async with self._lock:
            self._cache.clear()


# Global instance
memory_cache = MemoryCache()