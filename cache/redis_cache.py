import json
import time
from datetime import datetime
from typing import Any, Dict, Optional, Union

import redis

from cache.utils import (
    compress_data,
    decode_binary_data,
    decompress_data,
    encode_binary_data,
    get_ttl,
)
from config import Config


class RedisCache:
    """Redis cache implementation with compression and binary data support."""

    def __init__(self):
        """Initialize the Redis cache."""
        self.redis = redis.from_url(Config.REDIS_URL)
        self.stats_key = "wisp:cache:stats"
        self.prefix = "wisp:cache:"
        self.metadata_prefix = "wisp:metadata:"

        # Initialize stats if they don't exist
        if not self.redis.exists(self.stats_key):
            self.redis.hmset(self.stats_key, {"hits": 0, "misses": 0, "size": 0})

    def _get_cache_key(self, key: str) -> str:
        """Get the full cache key with prefix."""
        return f"{self.prefix}{key}"

    def _get_metadata_key(self, key: str) -> str:
        """Get the full metadata key with prefix."""
        return f"{self.metadata_prefix}{key}"

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get a value from the cache.

        Args:
            key: The cache key

        Returns:
            Optional[Dict]: The cached value or None if not found
        """
        cache_key = self._get_cache_key(key)
        data = self.redis.get(cache_key)

        if data is None:
            self.redis.hincrby(self.stats_key, "misses", 1)
            return None

        self.redis.hincrby(self.stats_key, "hits", 1)

        # Decompress and decode the data
        decompressed_data = decompress_data(data)
        if decompressed_data:
            return decode_binary_data(decompressed_data)

        return None

    def set(self, key: str, value: Dict[str, Any], ttl: Optional[Union[int, str]] = None) -> bool:
        """
        Set a value in the cache.

        Args:
            key: The cache key
            value: The value to cache
            ttl: Time to live in seconds

        Returns:
            bool: True if successful
        """
        # Validate and normalize TTL
        ttl = get_ttl(ttl)

        cache_key = self._get_cache_key(key)
        metadata_key = self._get_metadata_key(key)

        current_time = time.time()
        expires_at = current_time + ttl

        # Encode binary data and compress
        serializable_value = encode_binary_data(value)
        compressed_data = compress_data(serializable_value)

        # Store the data
        self.redis.setex(cache_key, ttl, compressed_data)

        # Store metadata
        metadata = {"stored_at": current_time, "expires_at": expires_at}
        self.redis.setex(metadata_key, ttl, json.dumps(metadata))

        # Update stats
        if not self.redis.exists(cache_key):
            self.redis.hincrby(self.stats_key, "size", 1)

        return True

    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.

        Args:
            key: The cache key

        Returns:
            bool: True if deleted, False if not found
        """
        cache_key = self._get_cache_key(key)
        metadata_key = self._get_metadata_key(key)

        if self.redis.exists(cache_key):
            self.redis.delete(cache_key)
            self.redis.delete(metadata_key)
            self.redis.hincrby(self.stats_key, "size", -1)
            return True

        return False

    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.

        Args:
            pattern: The pattern to match

        Returns:
            int: Number of keys deleted
        """
        cache_pattern = f"{self.prefix}{pattern}"
        metadata_pattern = f"{self.metadata_prefix}{pattern}"

        # Get all matching cache keys
        cache_keys = self.redis.keys(cache_pattern)
        metadata_keys = self.redis.keys(metadata_pattern)

        count = 0

        # Delete cache keys
        if cache_keys:
            count = len(cache_keys)
            self.redis.delete(*cache_keys)

        # Delete metadata keys
        if metadata_keys:
            self.redis.delete(*metadata_keys)

        # Update stats
        if count > 0:
            self.redis.hincrby(self.stats_key, "size", -count)

        return count

    def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a cached item.

        Args:
            key: The cache key

        Returns:
            Optional[Dict]: Metadata or None if not found
        """
        metadata_key = self._get_metadata_key(key)
        data = self.redis.get(metadata_key)

        if data is None:
            return None

        try:
            metadata = json.loads(data)
            return {
                "status": "hit",
                "stored_at": datetime.fromtimestamp(metadata["stored_at"]).isoformat(),
                "expires_at": datetime.fromtimestamp(metadata["expires_at"]).isoformat(),
            }
        except (json.JSONDecodeError, KeyError):
            return None

    def clear(self) -> bool:
        """
        Clear all cache data.

        Returns:
            bool: True if successful
        """
        # Get all cache keys
        keys = self.redis.keys(f"{self.prefix}*")
        metadata_keys = self.redis.keys(f"{self.metadata_prefix}*")

        if keys:
            self.redis.delete(*keys)

        if metadata_keys:
            self.redis.delete(*metadata_keys)

        # Reset stats
        self.redis.hset(self.stats_key, "size", 0)

        return True

    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.

        Returns:
            Dict[str, int]: Cache statistics
        """
        stats = self.redis.hgetall(self.stats_key)

        # Convert bytes to strings and values to integers
        return {k.decode("utf-8"): int(v) for k, v in stats.items()}
