import pytest
from http import HTTPStatus

from ..testdata import mock_filmlist
from ..settings import settings


pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {
                "page_size": "-5",
                "page_number": "1",
            },
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "length": 1,
            },  # должно придти сообщение об ошибке
        ),
        (
            {
                "page_size": "0",
                "page_number": "1",
            },
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "length": 1,
            },  # должно придти сообщение об ошибке
        ),
        (
            {
                "page_size": "some text",
                "page_number": "1",
            },
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "length": 1,
            },  # должно придти сообщение об ошибке
        ),
        (
            {
                "page_size": "3.14",
                "page_number": "1",
            },
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "length": 1,
            },  # должно придти сообщение об ошибке
        ),
        (
            {
                "page_size": "5",
                "page_number": "-1",
            },
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "length": 1,
            },  # должно придти сообщение об ошибке
        ),
        (
            {
                "page_size": "5",
                "page_number": "0",
            },
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "length": 1,
            },  # должно придти сообщение об ошибке
        ),
        (
            {
                "page_size": "5",
                "page_number": "some text",
            },
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "length": 1,
            },  # должно придти сообщение об ошибке
        ),
        (
            {
                "page_size": "5",
                "page_number": "3.14",
            },
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "length": 1,
            },  # должно придти сообщение об ошибке
        ),
        (
            {"page_size": "5", "page_number": "1"},
            {"status": HTTPStatus.OK, "length": 5},
        ),
        (None, {"status": HTTPStatus.OK, "length": 50}),  # пагинация по умолчанию
    ],
)
async def test_validate_values_and_get_only_N_entries(
    write_to_es,
    read_from_api,
    delete_test_data_from_es,
    query_data,
    expected_answer,
    redis_client,
):
    redis_client.flushall()
    await write_to_es(mock_filmlist.filmlist)
    status, body = await read_from_api("/films/", query_data)
    await delete_test_data_from_es(settings.index_movies)
    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]


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
            {"status": HTTPStatus.OK, "length": 8},
            # 8 - это число элементов словаря, описывающего один фильм
        ),
    ],
)
async def test_get_specific_entry(
    write_to_es,
    read_from_api,
    delete_test_data_from_es,
    query_data,
    expected_answer,
    redis_client,
):
    redis_client.flushall()
    await write_to_es(mock_filmlist.filmlist)
    uuid = (
        query_data["uuid"] or mock_filmlist.filmlist[0]["_id"]
    )  # если None, то задаем верное значение
    status, body = await read_from_api(f"/films/{uuid}")
    await delete_test_data_from_es(settings.index_movies)
    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]


async def test_get_all_entries(
    write_to_es,
    read_from_api,
    delete_test_data_from_es,
    redis_client,
):
    redis_client.flushall()
    await write_to_es(mock_filmlist.filmlist)
    status, body = await read_from_api("/films/?page_size=9999")
    await delete_test_data_from_es(settings.index_movies)
    assert status == HTTPStatus.OK
    assert len(body) == len(mock_filmlist.filmlist)


async def test_cache(
    write_to_es,
    read_from_api,
    delete_test_data_from_es,
    redis_client,
):
    redis_client.flushall()
    await write_to_es(mock_filmlist.filmlist)
    # читаем из еластика
    status, body = await read_from_api("/films/")
    await delete_test_data_from_es(settings.index_movies)
    assert status == HTTPStatus.OK
    assert len(body) == 50
    # читаем из кэша
    status, body = await read_from_api("/films/")
    assert status == HTTPStatus.OK
    assert len(body) == 50
