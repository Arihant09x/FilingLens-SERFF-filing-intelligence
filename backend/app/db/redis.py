# app/db/redis.py
from redis.asyncio import Redis
from app.core.config import settings

redis_client: Redis = Redis.from_url(
    settings.redis_url,
    protocol=2,
    encoding="utf-8",
    decode_responses=True,
)