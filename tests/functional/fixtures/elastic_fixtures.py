from typing import List
from http import HTTPStatus

import pytest
from elasticsearch import AsyncElasticsearch, helpers

from ..settings import settings
from ..testdata import es_index_movies, es_index_genres, es_index_persons


@pytest.fixture(scope="session")
async def es_client():
    client = AsyncElasticsearch(
        hosts=[f"{settings.elastic_host}:{settings.elastic_port}"],
    )
    if not (await client.indices.exists(index=settings.index_movies)):
        await client.indices.create(
            index=settings.index_movies,
            settings=es_index_movies.index["settings"],
            mappings=es_index_movies.index["mappings"],
        )
    if not (await client.indices.exists(index=settings.index_genres)):
        await client.indices.create(
            index=settings.index_genres,
            settings=es_index_genres.index["settings"],
            mappings=es_index_genres.index["mappings"],
        )
    if not (await client.indices.exists(index=settings.index_persons)):
        await client.indices.create(
            index=settings.index_persons,
            settings=es_index_persons.index["settings"],
            mappings=es_index_persons.index["mappings"],
        )
    yield client
    await client.indices.delete(
        index=settings.index_movies, ignore=HTTPStatus.NOT_FOUND.value
    )
    await client.indices.delete(
        index=settings.index_genres, ignore=HTTPStatus.NOT_FOUND.value
    )
    await client.indices.delete(
        index=settings.index_persons, ignore=HTTPStatus.NOT_FOUND.value
    )
    await client.close()


@pytest.fixture
async def write_to_es(es_client):
    async def inner(actions: List[dict]):
        okeys, _ = await helpers.async_bulk(
            client=es_client, actions=actions, refresh="wait_for"
        )
        if not okeys == len(actions):
            raise Exception("Ошибка записи тестовых данных в Elastic")

    return inner


@pytest.fixture
async def delete_test_data_from_es(es_client):
    async def inner(index_name: str):
        response = await es_client.delete_by_query(
            index=index_name, query={"match_all": {}}
        )
        if response["failures"]:
            raise Exception("Ошибка удаления тестовых данных из Elastic")

    return inner
