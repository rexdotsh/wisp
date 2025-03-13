from cache.memory_cache import MemoryCache
from cache.redis_cache import RedisCache
from config import Config


def get_cache():
    if Config.CACHE_TYPE == "redis":
        return RedisCache()
    return MemoryCache()


cache = get_cache()
