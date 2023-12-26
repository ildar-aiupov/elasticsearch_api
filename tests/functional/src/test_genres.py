import pytest
from http import HTTPStatus

from ..testdata import mock_genrelist
from ..settings import settings


pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {"uuid": "00000000-0000-0000-0000-000000000000"},
            {
                "status": HTTPStatus.NOT_FOUND,
                "length": 1,
            },  # должно придти сообщение NOT FOUND
        ),
        (
            {"uuid": None},  # верный uuid будет задан в тесте
            {"status": HTTPStatus.OK, "length": 2}
            # 2 - это число элементов словаря, описывающего один жанр
        ),
    ],
)
async def test_get_specific_genre(
    write_to_es,
    read_from_api,
    delete_test_data_from_es,
    query_data,
    expected_answer,
    redis_client,
):
    redis_client.flushall()
    await write_to_es(mock_genrelist.genrelist)
    uuid = (
        query_data["uuid"] or mock_genrelist.genrelist[0]["_id"]
    )  # если None, то задаем верное значение
    status, body = await read_from_api(f"/genres/{uuid}")
    await delete_test_data_from_es(settings.index_genres)
    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]


async def test_get_all_genres(
    write_to_es,
    read_from_api,
    delete_test_data_from_es,
    redis_client,
):
    redis_client.flushall()
    await write_to_es(mock_genrelist.genrelist)
    status, body = await read_from_api("/genres/")
    await delete_test_data_from_es(settings.index_genres)
    assert status == HTTPStatus.OK
    assert len(body) == len(mock_genrelist.genrelist)


async def test_cache_genres(
    write_to_es,
    read_from_api,
    delete_test_data_from_es,
    redis_client,
):
    redis_client.flushall()
    await write_to_es(mock_genrelist.genrelist)
    # читаем из еластика
    status, body = await read_from_api("/genres/")
    await delete_test_data_from_es(settings.index_genres)
    assert status == HTTPStatus.OK
    assert len(body) == len(mock_genrelist.genrelist)
    # читаем из кэша
    status, body = await read_from_api("/genres/")
    assert status == HTTPStatus.OK
    assert len(body) == len(mock_genrelist.genrelist)
