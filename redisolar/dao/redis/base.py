from redis.client import Redis

from redisolar.dao.redis.key_schema import KeySchema


class RedisDaoBase:
    """Shared functionality for Redis DAO classes."""

    def __init__(self,
                 redis_client: Redis,
                 key_schema: KeySchema = None, **kwargs) -> None:
        self.redis = redis_client
        if not key_schema:
            key_schema = KeySchema()
        self.key_schema = key_schema
