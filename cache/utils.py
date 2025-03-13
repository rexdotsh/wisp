import base64
import functools
import json
import zlib
from typing import Any, Dict, Optional, Union

from config import Config


def memoize(func):
    """Simple memoization decorator for functions with no arguments."""
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper


def get_ttl(ttl: Optional[Union[int, str]] = None) -> int:
    """
    Get a valid TTL value within the configured bounds.

    Args:
        ttl: The TTL value to validate (can be None, int, or string)

    Returns:
        int: A valid TTL value
    """
    if ttl is None:
        return Config.CACHE_DEFAULT_TTL

    # Convert string to int if needed
    if isinstance(ttl, str):
        try:
            ttl = int(ttl)
        except ValueError:
            return Config.CACHE_DEFAULT_TTL

    # Ensure TTL is within bounds
    if ttl < Config.CACHE_TTL_MIN or ttl > Config.CACHE_TTL_MAX:
        return Config.CACHE_DEFAULT_TTL

    return ttl


def compress_data(data: Any) -> bytes:
    """
    Compress data using zlib.

    Args:
        data: The data to compress

    Returns:
        bytes: Compressed data
    """
    if not Config.CACHE_COMPRESSION:
        return json.dumps(data).encode("utf-8")

    compressed = zlib.compress(json.dumps(data).encode("utf-8"))
    return compressed


def decompress_data(data: bytes) -> Any:
    """
    Decompress data using zlib.

    Args:
        data: The compressed data

    Returns:
        Any: Decompressed data
    """
    if not data:
        return None

    try:
        # Try to decompress (if compression is enabled)
        if Config.CACHE_COMPRESSION:
            decompressed = zlib.decompress(data)
            return json.loads(decompressed.decode("utf-8"))
        else:
            return json.loads(data.decode("utf-8"))
    except (zlib.error, json.JSONDecodeError):
        # Fallback to regular JSON decoding if decompression fails
        try:
            return json.loads(data.decode("utf-8"))
        except json.JSONDecodeError:
            return None


def encode_binary_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Encode binary data in a dictionary to base64.

    Args:
        data: Dictionary that may contain binary data

    Returns:
        Dict: Dictionary with binary data encoded to base64
    """
    if not isinstance(data, dict):
        return data

    result = {}
    for key, value in data.items():
        if isinstance(value, bytes):
            result[key] = base64.b64encode(value).decode("utf-8")
        elif isinstance(value, dict):
            result[key] = encode_binary_data(value)
        else:
            result[key] = value

    return result


def decode_binary_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Decode base64 encoded data in a dictionary back to binary.

    Args:
        data: Dictionary that may contain base64 encoded data

    Returns:
        Dict: Dictionary with base64 data decoded to binary
    """
    if not isinstance(data, dict):
        return data

    result = {}
    for key, value in data.items():
        if key == "image_data" and isinstance(value, str):
            try:
                result[key] = base64.b64decode(value)
            except Exception:
                result[key] = value
        elif isinstance(value, dict):
            result[key] = decode_binary_data(value)
        else:
            result[key] = value

    return result
