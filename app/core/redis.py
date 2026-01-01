from redis.asyncio import Redis
from .config import settings

JTI_EXPIRE = int(settings.REFRESH_TOKEN_EXPIRE_DAYS) * 24 * 60 * 60
redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)


async def add_token_to_blocklist(jti: str) -> None:

    await redis.set(name=jti, value="", ex=JTI_EXPIRE)


async def token_in_blocklist(jti: str) -> bool:
    value = await redis.get(jti)

    return value is not None
