import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # flask settings
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-in-production")

    # cache settings
    CACHE_TYPE = os.getenv("CACHE_TYPE", "memory")  # 'memory' or 'redis'
    CACHE_DEFAULT_TTL = int(os.getenv("CACHE_DEFAULT_TTL", 3600))  # 1 hour
    CACHE_TTL_MIN = int(os.getenv("CACHE_TTL_MIN", 3600))  # 1 hour
    CACHE_TTL_MAX = int(os.getenv("CACHE_TTL_MAX", 2419200))  # 28 days
    CACHE_COMPRESSION = os.getenv("CACHE_COMPRESSION", "True").lower() == "true"
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # avatar settings
    AVATAR_TIMEOUT = int(os.getenv("AVATAR_TIMEOUT", 10000))  # 10 seconds
