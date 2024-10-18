from ..settings import env

CACHES = {
    "default": {
        "BACKEND": "redis_cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://localhost:6379/0"),
    }
}
