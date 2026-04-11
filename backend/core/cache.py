"""
Redis cache implementation for spatial query optimization.

Provides caching for scores, hex grids, isochrones, and spatial statistics
with appropriate TTL policies and cache key strategies.
"""

import json
import hashlib
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import timedelta

from redis.asyncio import Redis
from pydantic import BaseModel

from config import settings

logger = logging.getLogger(__name__)


class CacheKeyBuilder:
    """Builds consistent cache keys for different data types."""
    
    @staticmethod
    def score_key(lat: float, lng: float, weights: Dict[str, float]) -> str:
        """Generate cache key for site scores."""
        weights_hash = hashlib.md5(
            json.dumps(weights, sort_keys=True).encode()
        ).hexdigest()[:8]
        return f"spatial:scores:{lat:.6f}:{lng:.6f}:{weights_hash}"
    
    @staticmethod
    def hex_grid_key(resolution: int, use_case: str, weights: Optional[Dict[str, float]] = None) -> str:
        """Generate cache key for hex grid data."""
        if weights:
            weights_hash = hashlib.md5(
                json.dumps(weights, sort_keys=True).encode()
            ).hexdigest()[:8]
            return f"spatial:hex_grid:{resolution}:{use_case}:{weights_hash}"
        return f"spatial:hex_grid:{resolution}:{use_case}"
    
    @staticmethod
    def isochrone_key(lat: float, lng: float, mode: str, minutes: int) -> str:
        """Generate cache key for isochrone data."""
        return f"spatial:isochrones:{lat:.6f}:{lng:.6f}:{mode}:{minutes}"
    
    @staticmethod
    def statistics_key(layer: str) -> str:
        """Generate cache key for layer statistics."""
        return f"stats:{layer}"
    
    @staticmethod
    def cluster_key(algorithm: str, params: Dict[str, Any]) -> str:
        """Generate cache key for clustering results."""
        params_hash = hashlib.md5(
            json.dumps(params, sort_keys=True).encode()
        ).hexdigest()[:8]
        return f"spatial:clusters:{algorithm}:{params_hash}"
    
    @staticmethod
    def hotspot_key(layer: str, confidence: float) -> str:
        """Generate cache key for hotspot analysis."""
        return f"spatial:hotspots:{layer}:{confidence}"


class CacheConfig:
    """Cache configuration with TTL policies."""
    
    # TTL values in seconds
    SCORE_TTL = 3600  # 1 hour
    HEX_GRID_TTL = 86400  # 24 hours
    ISOCHRONE_TTL = 21600  # 6 hours
    STATISTICS_TTL = 86400  # 24 hours
    CLUSTER_TTL = 7200  # 2 hours
    HOTSPOT_TTL = 14400  # 4 hours
    
    # Cache size limits
    MAX_CACHE_SIZE = 512 * 1024 * 1024  # 512MB
    MAX_KEY_LENGTH = 250


class SpatialCache:
    """Redis-based cache for spatial query optimization."""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.key_builder = CacheKeyBuilder()
        self.config = CacheConfig()
    
    async def get_score(self, lat: float, lng: float, weights: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """Get cached site score."""
        key = self.key_builder.score_key(lat, lng, weights)
        try:
            cached_data = await self.redis.get(key)
            if cached_data:
                logger.debug(f"Cache hit for score: {key}")
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache get error for score {key}: {e}")
        return None
    
    async def set_score(self, lat: float, lng: float, weights: Dict[str, float], 
                       score_data: Dict[str, Any]) -> bool:
        """Cache site score with TTL."""
        key = self.key_builder.score_key(lat, lng, weights)
        try:
            await self.redis.setex(
                key, 
                self.config.SCORE_TTL, 
                json.dumps(score_data, default=str)
            )
            logger.debug(f"Cached score: {key}")
            return True
        except Exception as e:
            logger.warning(f"Cache set error for score {key}: {e}")
            return False
    
    async def get_hex_grid(self, resolution: int, use_case: str, 
                          weights: Optional[Dict[str, float]] = None) -> Optional[Dict[str, Any]]:
        """Get cached hex grid data."""
        key = self.key_builder.hex_grid_key(resolution, use_case, weights)
        try:
            cached_data = await self.redis.get(key)
            if cached_data:
                logger.debug(f"Cache hit for hex grid: {key}")
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache get error for hex grid {key}: {e}")
        return None
    
    async def set_hex_grid(self, resolution: int, use_case: str, hex_data: Dict[str, Any],
                          weights: Optional[Dict[str, float]] = None) -> bool:
        """Cache hex grid data with TTL."""
        key = self.key_builder.hex_grid_key(resolution, use_case, weights)
        try:
            await self.redis.setex(
                key,
                self.config.HEX_GRID_TTL,
                json.dumps(hex_data, default=str)
            )
            logger.debug(f"Cached hex grid: {key}")
            return True
        except Exception as e:
            logger.warning(f"Cache set error for hex grid {key}: {e}")
            return False
    
    async def get_isochrone(self, lat: float, lng: float, mode: str, 
                           minutes: int) -> Optional[Dict[str, Any]]:
        """Get cached isochrone data."""
        key = self.key_builder.isochrone_key(lat, lng, mode, minutes)
        try:
            cached_data = await self.redis.get(key)
            if cached_data:
                logger.debug(f"Cache hit for isochrone: {key}")
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache get error for isochrone {key}: {e}")
        return None
    
    async def set_isochrone(self, lat: float, lng: float, mode: str, minutes: int,
                           isochrone_data: Dict[str, Any]) -> bool:
        """Cache isochrone data with TTL."""
        key = self.key_builder.isochrone_key(lat, lng, mode, minutes)
        try:
            await self.redis.setex(
                key,
                self.config.ISOCHRONE_TTL,
                json.dumps(isochrone_data, default=str)
            )
            logger.debug(f"Cached isochrone: {key}")
            return True
        except Exception as e:
            logger.warning(f"Cache set error for isochrone {key}: {e}")
            return False
    
    async def get_statistics(self, layer: str) -> Optional[Dict[str, Any]]:
        """Get cached layer statistics."""
        key = self.key_builder.statistics_key(layer)
        try:
            cached_data = await self.redis.get(key)
            if cached_data:
                logger.debug(f"Cache hit for statistics: {key}")
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache get error for statistics {key}: {e}")
        return None
    
    async def set_statistics(self, layer: str, stats_data: Dict[str, Any]) -> bool:
        """Cache layer statistics with TTL."""
        key = self.key_builder.statistics_key(layer)
        try:
            await self.redis.setex(
                key,
                self.config.STATISTICS_TTL,
                json.dumps(stats_data, default=str)
            )
            logger.debug(f"Cached statistics: {key}")
            return True
        except Exception as e:
            logger.warning(f"Cache set error for statistics {key}: {e}")
            return False
    
    async def get_clusters(self, algorithm: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached clustering results."""
        key = self.key_builder.cluster_key(algorithm, params)
        try:
            cached_data = await self.redis.get(key)
            if cached_data:
                logger.debug(f"Cache hit for clusters: {key}")
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache get error for clusters {key}: {e}")
        return None
    
    async def set_clusters(self, algorithm: str, params: Dict[str, Any], 
                          cluster_data: Dict[str, Any]) -> bool:
        """Cache clustering results with TTL."""
        key = self.key_builder.cluster_key(algorithm, params)
        try:
            await self.redis.setex(
                key,
                self.config.CLUSTER_TTL,
                json.dumps(cluster_data, default=str)
            )
            logger.debug(f"Cached clusters: {key}")
            return True
        except Exception as e:
            logger.warning(f"Cache set error for clusters {key}: {e}")
            return False
    
    async def get_hotspots(self, layer: str, confidence: float) -> Optional[Dict[str, Any]]:
        """Get cached hotspot analysis."""
        key = self.key_builder.hotspot_key(layer, confidence)
        try:
            cached_data = await self.redis.get(key)
            if cached_data:
                logger.debug(f"Cache hit for hotspots: {key}")
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache get error for hotspots {key}: {e}")
        return None
    
    async def set_hotspots(self, layer: str, confidence: float, 
                          hotspot_data: Dict[str, Any]) -> bool:
        """Cache hotspot analysis with TTL."""
        key = self.key_builder.hotspot_key(layer, confidence)
        try:
            await self.redis.setex(
                key,
                self.config.HOTSPOT_TTL,
                json.dumps(hotspot_data, default=str)
            )
            logger.debug(f"Cached hotspots: {key}")
            return True
        except Exception as e:
            logger.warning(f"Cache set error for hotspots {key}: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache keys matching pattern."""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info(f"Invalidated {deleted} cache keys matching pattern: {pattern}")
                return deleted
        except Exception as e:
            logger.warning(f"Cache invalidation error for pattern {pattern}: {e}")
        return 0
    
    async def invalidate_scores(self) -> int:
        """Invalidate all cached scores."""
        return await self.invalidate_pattern("spatial:scores:*")
    
    async def invalidate_hex_grids(self) -> int:
        """Invalidate all cached hex grids."""
        return await self.invalidate_pattern("spatial:hex_grid:*")
    
    async def invalidate_statistics(self) -> int:
        """Invalidate all cached statistics."""
        return await self.invalidate_pattern("stats:*")
    
    async def get_cache_info(self) -> Dict[str, Any]:
        """Get cache usage information."""
        try:
            info = await self.redis.info("memory")
            keyspace = await self.redis.info("keyspace")
            
            # Count keys by pattern
            score_keys = len(await self.redis.keys("spatial:scores:*"))
            hex_keys = len(await self.redis.keys("spatial:hex_grid:*"))
            isochrone_keys = len(await self.redis.keys("spatial:isochrones:*"))
            stats_keys = len(await self.redis.keys("stats:*"))
            
            return {
                "memory_used": info.get("used_memory_human", "unknown"),
                "memory_peak": info.get("used_memory_peak_human", "unknown"),
                "total_keys": keyspace.get("db0", {}).get("keys", 0),
                "key_counts": {
                    "scores": score_keys,
                    "hex_grids": hex_keys,
                    "isochrones": isochrone_keys,
                    "statistics": stats_keys
                },
                "hit_rate": "calculated_separately"  # Would need separate tracking
            }
        except Exception as e:
            logger.warning(f"Error getting cache info: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> bool:
        """Check if Redis cache is healthy."""
        try:
            await self.redis.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False


# Global cache instance
from core.database import redis_client
spatial_cache = SpatialCache(redis_client)


# Cache decorators for common patterns
def cache_score(ttl: int = CacheConfig.SCORE_TTL):
    """Decorator to cache scoring function results."""
    def decorator(func):
        async def wrapper(lat: float, lng: float, weights: Dict[str, float], *args, **kwargs):
            # Try cache first
            cached_result = await spatial_cache.get_score(lat, lng, weights)
            if cached_result:
                return cached_result
            
            # Compute and cache result
            result = await func(lat, lng, weights, *args, **kwargs)
            await spatial_cache.set_score(lat, lng, weights, result)
            return result
        return wrapper
    return decorator


def cache_hex_grid(ttl: int = CacheConfig.HEX_GRID_TTL):
    """Decorator to cache hex grid computation results."""
    def decorator(func):
        async def wrapper(resolution: int, use_case: str, weights: Optional[Dict[str, float]] = None, *args, **kwargs):
            # Try cache first
            cached_result = await spatial_cache.get_hex_grid(resolution, use_case, weights)
            if cached_result:
                return cached_result
            
            # Compute and cache result
            result = await func(resolution, use_case, weights, *args, **kwargs)
            await spatial_cache.set_hex_grid(resolution, use_case, result, weights)
            return result
        return wrapper
    return decorator


def cache_statistics(ttl: int = CacheConfig.STATISTICS_TTL):
    """Decorator to cache statistics computation results."""
    def decorator(func):
        async def wrapper(layer: str, *args, **kwargs):
            # Try cache first
            cached_result = await spatial_cache.get_statistics(layer)
            if cached_result:
                return cached_result
            
            # Compute and cache result
            result = await func(layer, *args, **kwargs)
            await spatial_cache.set_statistics(layer, result)
            return result
        return wrapper
    return decorator