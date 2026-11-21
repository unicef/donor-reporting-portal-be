from urllib.parse import urlparse, urlunparse

from ..settings import env

GRAPH_CACHE_TTL = env.int("GRAPH_CACHE_TTL", default=0)

redis_url = env("REDIS_URL", default="redis://localhost:6379/0")
cache_url = env("REDIS_CACHE_URL", default=None)
if not cache_url:
    cache_url = urlunparse(urlparse(redis_url)._replace(path="/2"))

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": cache_url,
        "TIMEOUT": env.int("CACHE_TIMEOUT", default=300),
        "KEY_PREFIX": "drp",
        "VERSION": 1,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            "CONNECTION_POOL_KWARGS": {"max_connections": 50},
        },
    }
}
