# app/db/redis.py
from redis.asyncio import Redis
from app.core.config import settings

redis_client: Redis = Redis.from_url(
    settings.redis_url,
    protocol=2,
    socket_connect_timeout=10,
    socket_timeout=30,
    encoding="utf-8",
    decode_responses=True,
)