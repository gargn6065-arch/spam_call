import redis.asyncio as redis
import os
import json
from typing import Optional, Any

class CacheService:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.use_redis = True
        try:
            self.redis = redis.from_url(redis_url, decode_responses=True)
        except Exception as e:
            print(f"Redis connection failed: {e}. Falling back to in-memory cache.")
            self.use_redis = False
            self.memory_cache = {}

    async def get(self, key: str) -> Optional[Any]:
        if self.use_redis:
            try:
                data = await self.redis.get(key)
                if data:
                    return json.loads(data)
            except Exception as e:
                print(f"Redis get error: {e}")
        else:
            data = self.memory_cache.get(key)
            if data:
                return json.loads(data)
        return None

    async def set(self, key: str, value: Any, expire: int = 3600):
        if self.use_redis:
            try:
                await self.redis.set(key, json.dumps(value), ex=expire)
            except Exception as e:
                print(f"Redis set error: {e}")
        else:
            self.memory_cache[key] = json.dumps(value)

    async def close(self):
        if self.use_redis:
            await self.redis.close()
