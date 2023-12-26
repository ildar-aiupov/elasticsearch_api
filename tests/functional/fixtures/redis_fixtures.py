import pytest

from redis import Redis

from ..settings import settings


@pytest.fixture(scope="session")
def redis_client():
    client = Redis(host=settings.redis_host, port=settings.redis_port)
    yield client
    client.close()
