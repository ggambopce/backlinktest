import os
from redis.asyncio import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# 간단하게 전역 싱글톤처럼 사용
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)


async def get_redis() -> Redis:
    """
    FastAPI Depends 에서 사용하는 의존성 함수.
    """
    return redis_client
