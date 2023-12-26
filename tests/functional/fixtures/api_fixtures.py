import aiohttp
import pytest

from ..settings import settings


@pytest.fixture
async def read_from_api():
    async def inner(append_url: str, params: dict = None):
        async with aiohttp.ClientSession() as session:
            url = settings.base_api_url + append_url
            async with session.get(url, params=params) as response:
                status = response.status
                body = await response.json()
        return status, body

    return inner
