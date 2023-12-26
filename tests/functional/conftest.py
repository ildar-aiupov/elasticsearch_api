import asyncio

import pytest

from .fixtures.api_fixtures import read_from_api
from .fixtures.elastic_fixtures import es_client, write_to_es, delete_test_data_from_es
from .fixtures.redis_fixtures import redis_client


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
