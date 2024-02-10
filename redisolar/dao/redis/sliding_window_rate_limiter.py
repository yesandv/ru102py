import datetime
import random
from redis.client import Redis

from redisolar.dao.base import RateLimiterDaoBase
from redisolar.dao.redis.base import RedisDaoBase
from redisolar.dao.redis.key_schema import KeySchema

from redisolar.dao.base import RateLimitExceededException


class SlidingWindowRateLimiter(RateLimiterDaoBase, RedisDaoBase):
    """A sliding-window rate-limiter."""

    def __init__(
            self,
            window_size_ms: int,
            max_hits: int,
            redis_client: Redis,
            key_schema: KeySchema = None,
            **kwargs
    ):
        self.window_size_ms = window_size_ms
        self.max_hits = max_hits
        super().__init__(redis_client, key_schema, **kwargs)

    def hit(self, name: str):
        """Record a hit using the rate-limiter."""
        key = self.key_schema.sliding_window_rate_limiter_key(
            name,
            self.window_size_ms,
            self.max_hits,
        )
        current_time_ms = datetime.datetime.now().timestamp() * 1000

        pipeline = self.redis.pipeline()
        pipeline.zadd(key, mapping={str(complex(random.random())): current_time_ms})
        pipeline.zremrangebyscore(key, 0, current_time_ms - self.window_size_ms)
        pipeline.zcard(key)
        _, _, hits = pipeline.execute()

        if hits > self.max_hits:
            raise RateLimitExceededException()
