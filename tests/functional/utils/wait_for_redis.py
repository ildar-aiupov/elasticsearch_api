import sys
import logging

import backoff
import redis

sys.path.append("..")
from settings import settings


def backoff_message(detail):
    logging.getLogger("my-logger").warning("Redis is not ready. Waiting...")


@backoff.on_exception(
    wait_gen=backoff.expo,
    exception=redis.ConnectionError,
    on_backoff=backoff_message,
    max_time=settings.redis_waiter_timelimit,
)
def wait_for_redis(redis):
    redis.ping()


if __name__ == "__main__":
    redis = redis.Redis(host=settings.redis_host, port=settings.redis_port)
    wait_for_redis(redis)
    logging.getLogger("my-logger").warning("Redis is ready")
