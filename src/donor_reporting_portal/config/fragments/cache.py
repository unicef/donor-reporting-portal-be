import os

from ..settings import env

os.environ["GRAPH_CACHE_TTL"] = "0"
GRAPH_CACHE_TTL = 0

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://localhost:6379/0"),
    }
}
