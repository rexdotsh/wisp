import re
import time
from datetime import datetime
from typing import Any, Dict, Optional, Union

from cache.utils import decode_binary_data, encode_binary_data, get_ttl


class MemoryCache:
    """In-memory cache implementation with binary data support."""

    def __init__(self):
        """Initialize the memory cache."""
        self.cache = {}
        self.stats = {"hits": 0, "misses": 0, "size": 0}
        self.prefix = "wisp:cache:"
        self.metadata_prefix = "wisp:metadata:"

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

        if cache_key not in self.cache:
            self.stats["misses"] += 1
            return None

        cache_item = self.cache[cache_key]
        current_time = time.time()

        if cache_item["expires_at"] < current_time:
            self.delete(key)
            self.stats["misses"] += 1
            return None

        self.stats["hits"] += 1
        # Handle binary data decoding
        if cache_item["data"]:
            return decode_binary_data(cache_item["data"])
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

        # Encode binary data
        serializable_value = encode_binary_data(value)

        if cache_key not in self.cache:
            self.stats["size"] += 1

        self.cache[cache_key] = {
            "data": serializable_value,
            "stored_at": current_time,
            "expires_at": expires_at,
        }

        # Store metadata separately
        self.cache[metadata_key] = {
            "data": {"stored_at": current_time, "expires_at": expires_at},
            "stored_at": current_time,
            "expires_at": expires_at,
        }

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

        deleted = False

        if cache_key in self.cache:
            del self.cache[cache_key]
            deleted = True

        if metadata_key in self.cache:
            del self.cache[metadata_key]

        if deleted:
            self.stats["size"] -= 1
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
        pattern = pattern.replace("*", ".*")
        regex = re.compile(f"{self.prefix}{pattern}")

        keys_to_delete = [key for key in self.cache.keys() if regex.match(key)]
        count = 0

        for key in keys_to_delete:
            # Extract the original key without prefix
            original_key = key[len(self.prefix) :]
            if self.delete(original_key):
                count += 1

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

        if metadata_key not in self.cache:
            return None

        cache_item = self.cache[metadata_key]
        current_time = time.time()

        if cache_item["expires_at"] < current_time:
            self.delete(key)
            return None

        metadata = cache_item["data"]
        return {
            "status": "hit",
            "stored_at": datetime.fromtimestamp(metadata["stored_at"]).isoformat(),
            "expires_at": datetime.fromtimestamp(metadata["expires_at"]).isoformat(),
        }

    def clear(self) -> bool:
        """
        Clear all cache data.

        Returns:
            bool: True if successful
        """
        self.cache = {}
        self.stats["size"] = 0
        return True

    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.

        Returns:
            Dict[str, int]: Cache statistics
        """
        return self.stats
