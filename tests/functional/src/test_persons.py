import pytest
from http import HTTPStatus

from ..testdata import mock_personlist, mock_filmlist
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
async def test_validate_values_and_get_only_N_persons(
    write_to_es,
    read_from_api,
    delete_test_data_from_es,
    query_data,
    expected_answer,
    redis_client,
):
    redis_client.flushall()
    await write_to_es(mock_personlist.personlist)
    status, body = await read_from_api("/persons/search", query_data)
    await delete_test_data_from_es(settings.index_persons)
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
            {"status": HTTPStatus.OK, "length": 40}
            # 40 - число элементов списка фильмов
        ),
    ],
)
async def test_get_films_by_person(
    write_to_es,
    read_from_api,
    delete_test_data_from_es,
    query_data,
    expected_answer,
    redis_client,
):
    redis_client.flushall()
    await write_to_es(mock_filmlist.filmlist[:40])
    uuid = (
        query_data["uuid"] or mock_filmlist.filmlist[0]["_source"]["actors"][0]["uuid"]
    )  # если None, то задаем верное значение
    status, body = await read_from_api(f"/persons/{uuid}/film")
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
            {"status": HTTPStatus.OK, "length": 3}
            # 3 - число элементов словаря, описывающего одну персону
        ),
    ],
)
async def test_get_specific_person(
    write_to_es,
    read_from_api,
    delete_test_data_from_es,
    query_data,
    expected_answer,
    redis_client,
):
    redis_client.flushall()
    await write_to_es(mock_personlist.personlist)
    uuid = (
        query_data["uuid"] or mock_personlist.personlist[0]["_id"]
    )  # если None, то задаем верное значение
    status, body = await read_from_api(f"/persons/{uuid}")
    await delete_test_data_from_es(settings.index_persons)
    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]


async def test_get_all_persons(
    write_to_es,
    read_from_api,
    delete_test_data_from_es,
    redis_client,
):
    redis_client.flushall()
    await write_to_es(mock_personlist.personlist)
    status, body = await read_from_api("/persons/search?page_size=9999")
    await delete_test_data_from_es(settings.index_persons)
    assert status == HTTPStatus.OK
    assert len(body) == len(mock_personlist.personlist)


async def test_cache_persons(
    write_to_es,
    read_from_api,
    delete_test_data_from_es,
    redis_client,
):
    redis_client.flushall()
    await write_to_es(mock_personlist.personlist)
    # читаем из еластика
    status, body = await read_from_api("/persons/search/")
    await delete_test_data_from_es(settings.index_persons)
    assert status == HTTPStatus.OK
    assert len(body) == 50
    # читаем из кэша
    status, body = await read_from_api("/persons/search/")
    assert status == HTTPStatus.OK
    assert len(body) == 50
