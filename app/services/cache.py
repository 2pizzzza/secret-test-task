import redis
from app.config import settings

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=True
)

def set_secret(key: str, value: str, ttl: int = 300):
    redis_client.setex(key, ttl, value)

def get_secret(key: str) -> str | None:
    return redis_client.get(key)

def delete_secret(key: str):
    redis_client.delete(key)