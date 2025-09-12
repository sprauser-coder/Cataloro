"""
Redis Caching Service for Cataloro Marketplace
Implements caching for sessions, listings, and frequently accessed data
"""

import json
import redis.asyncio as redis
from typing import Optional, Any, List, Dict
import logging
from datetime import timedelta
import os

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        # Redis connection settings
        self.redis_host = os.environ.get('REDIS_HOST', 'localhost')
        self.redis_port = int(os.environ.get('REDIS_PORT', 6379))
        self.redis_db = int(os.environ.get('REDIS_DB', 0))
        self.redis_password = os.environ.get('REDIS_PASSWORD', None)
        
        self.redis_client: Optional[redis.Redis] = None
        
        # Cache TTL settings (in seconds)
        self.TTL_SHORT = 300      # 5 minutes - for frequently changing data
        self.TTL_MEDIUM = 1800    # 30 minutes - for semi-static data
        self.TTL_LONG = 3600      # 1 hour - for static data
        self.TTL_SESSION = 86400  # 24 hours - for user sessions
    
    async def connect(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = await redis.from_url(
                f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}",
                password=self.redis_password,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("✅ Redis connection established successfully")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
            logger.info("📝 Continuing without cache (fallback mode)")
            self.redis_client = None
            return False
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")
    
    def _get_key(self, prefix: str, identifier: str) -> str:
        """Generate standardized cache key"""
        return f"cataloro:{prefix}:{identifier}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            return None
            
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with optional TTL"""
        if not self.redis_client:
            return False
            
        try:
            json_value = json.dumps(value, default=str)
            if ttl:
                await self.redis_client.setex(key, ttl, json_value)
            else:
                await self.redis_client.set(key, json_value)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis_client:
            return False
            
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.redis_client:
            return 0
            
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
            return 0
    
    # User Session Caching
    async def cache_user_session(self, user_id: str, user_data: Dict) -> bool:
        """Cache user session data"""
        key = self._get_key("session", user_id)
        return await self.set(key, user_data, self.TTL_SESSION)
    
    async def get_user_session(self, user_id: str) -> Optional[Dict]:
        """Get cached user session"""
        key = self._get_key("session", user_id)
        return await self.get(key)
    
    async def invalidate_user_session(self, user_id: str) -> bool:
        """Invalidate user session"""
        key = self._get_key("session", user_id)
        return await self.delete(key)
    
    # Listings Caching
    async def cache_listings(self, cache_key: str, listings: List[Dict]) -> bool:
        """Cache listings data"""
        key = self._get_key("listings", cache_key)
        return await self.set(key, listings, self.TTL_SHORT)
    
    async def get_cached_listings(self, cache_key: str) -> Optional[List[Dict]]:
        """Get cached listings"""
        key = self._get_key("listings", cache_key)
        return await self.get(key)
    
    async def invalidate_listings_cache(self) -> int:
        """Invalidate all listings cache"""
        pattern = self._get_key("listings", "*")
        return await self.delete_pattern(pattern)
    
    # User Profile Caching
    async def cache_user_profile(self, user_id: str, profile_data: Dict) -> bool:
        """Cache user profile data"""
        key = self._get_key("profile", user_id)
        return await self.set(key, profile_data, self.TTL_MEDIUM)
    
    async def get_cached_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get cached user profile"""
        key = self._get_key("profile", user_id)
        return await self.get(key)
    
    async def invalidate_user_profile(self, user_id: str) -> bool:
        """Invalidate user profile cache"""
        key = self._get_key("profile", user_id)
        return await self.delete(key)
    
    # Dashboard Data Caching
    async def cache_dashboard_data(self, data: Dict) -> bool:
        """Cache admin dashboard data"""
        key = self._get_key("dashboard", "admin")
        return await self.set(key, data, self.TTL_SHORT)
    
    async def get_cached_dashboard_data(self) -> Optional[Dict]:
        """Get cached dashboard data"""
        key = self._get_key("dashboard", "admin")
        return await self.get(key)
    
    async def invalidate_dashboard_cache(self) -> bool:
        """Invalidate dashboard cache"""
        key = self._get_key("dashboard", "admin")
        return await self.delete(key)
    
    # Search Results Caching
    async def cache_search_results(self, search_params: str, results: List[Dict]) -> bool:
        """Cache search results"""
        key = self._get_key("search", search_params)
        return await self.set(key, results, self.TTL_SHORT)
    
    async def get_cached_search_results(self, search_params: str) -> Optional[List[Dict]]:
        """Get cached search results"""
        key = self._get_key("search", search_params)
        return await self.get(key)
    
    # Basket/Cart Caching
    async def cache_user_baskets(self, user_id: str, baskets: List[Dict]) -> bool:
        """Cache user baskets"""
        key = self._get_key("baskets", user_id)
        return await self.set(key, baskets, self.TTL_SHORT)
    
    async def get_cached_user_baskets(self, user_id: str) -> Optional[List[Dict]]:
        """Get cached user baskets"""
        key = self._get_key("baskets", user_id)
        return await self.get(key)
    
    async def invalidate_user_baskets(self, user_id: str) -> bool:
        """Invalidate user baskets cache"""
        key = self._get_key("baskets", user_id)
        return await self.delete(key)
    
    # Notification Caching
    async def cache_user_notifications(self, user_id: str, notifications: List[Dict]) -> bool:
        """Cache user notifications"""
        key = self._get_key("notifications", user_id)
        return await self.set(key, notifications, self.TTL_SHORT)
    
    async def get_cached_user_notifications(self, user_id: str) -> Optional[List[Dict]]:
        """Get cached user notifications"""
        key = self._get_key("notifications", user_id)
        return await self.get(key)
    
    async def invalidate_user_notifications(self, user_id: str) -> bool:
        """Invalidate user notifications cache"""
        key = self._get_key("notifications", user_id)
        return await self.delete(key)
    
    # Health Check
    async def health_check(self) -> Dict[str, Any]:
        """Check cache service health"""
        if not self.redis_client:
            return {
                "status": "disabled",
                "message": "Redis not connected - running in fallback mode"
            }
        
        try:
            await self.redis_client.ping()
            info = await self.redis_client.info("memory")
            return {
                "status": "healthy",
                "connected": True,
                "memory_used": info.get("used_memory_human", "unknown"),
                "total_keys": await self.redis_client.dbsize()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

# Global cache service instance
cache_service = CacheService()

async def init_cache():
    """Initialize cache service"""
    await cache_service.connect()

async def cleanup_cache():
    """Cleanup cache service"""
    await cache_service.disconnect()