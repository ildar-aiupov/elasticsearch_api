from elasticsearch import AsyncElasticsearch, NotFoundError

from core.config import settings
from models.film import Film
from models.genre import Genre
from models.person import Person
from .storage_interface import StorageInterface


class AsyncElasticSearchEngine(StorageInterface):
    connection: AsyncElasticsearch

    def __init__(self):
        self.connection = AsyncElasticsearch(
            hosts=[f"{settings.elastic_host}:{settings.elastic_port}"]
        )

    async def close(self) -> None:
        await self.connection.close()

    async def get_entry(self, params: dict) -> Film | Genre | Person | None:
        index = params.get("index")
        id = params.get("id")
        try:
            doc = await self.connection.get(index=index, id=id)
            if index == settings.index_movies:
                return Film(**doc["_source"])
            if index == settings.index_genres:
                return Genre(**doc["_source"])
            if index == settings.index_persons:
                return Person(**doc["_source"])
        except NotFoundError:
            return None

    async def get_list(self, params: dict) -> list[Film | Genre | Person] | None:
        # из-за разных структур индексов еластика, разных query-параметров и разных
        # модельных классов для каждого ресурса нужен свой обработчик списка
        index = params.get("index")
        if index == settings.index_movies:
            return await self.get_list_movies(params=params)
        if index == settings.index_genres:
            return await self.get_list_genres(params=params)
        if index == settings.index_persons:
            return await self.get_list_persons(params=params)

    async def get_list_movies(self, params: dict) -> list[Film] | None:
        genre = params.get("genre")
        query = params.get("query")
        person_id = params.get("person_id")
        page_size = params.get("page_size")
        page_number = params.get("page_number")
        sort = params.get("sort")
        try:
            if genre:
                body = {
                    "query": {
                        "nested": {
                            "path": "genre",
                            "query": {
                                "bool": {"must": [{"term": {"genre.uuid": genre}}]}
                            },
                        }
                    }
                }
            elif query:
                body = {
                    "query": {
                        "bool": {
                            "should": [
                                {"match": {"title": query}},
                                {"match": {"description": query}},
                                {
                                    "nested": {
                                        "path": "genre",
                                        "query": {
                                            "bool": {
                                                "must": [
                                                    {"match": {"genre.name": query}}
                                                ]
                                            }
                                        },
                                    }
                                },
                                {
                                    "nested": {
                                        "path": "actors",
                                        "query": {
                                            "bool": {
                                                "must": [
                                                    {
                                                        "match": {
                                                            "actors.full_name": query
                                                        }
                                                    }
                                                ]
                                            }
                                        },
                                    }
                                },
                                {
                                    "nested": {
                                        "path": "writers",
                                        "query": {
                                            "bool": {
                                                "must": [
                                                    {
                                                        "match": {
                                                            "writers.full_name": query
                                                        }
                                                    }
                                                ]
                                            }
                                        },
                                    }
                                },
                                {
                                    "nested": {
                                        "path": "directors",
                                        "query": {
                                            "bool": {
                                                "must": [
                                                    {
                                                        "match": {
                                                            "directors.full_name": query
                                                        }
                                                    }
                                                ]
                                            }
                                        },
                                    }
                                },
                            ]
                        }
                    }
                }
            elif person_id:
                body = {
                    "query": {
                        "bool": {
                            "should": [
                                {
                                    "nested": {
                                        "path": "actors",
                                        "query": {
                                            "bool": {
                                                "must": [
                                                    {"term": {"actors.uuid": person_id}}
                                                ]
                                            }
                                        },
                                    }
                                },
                                {
                                    "nested": {
                                        "path": "writers",
                                        "query": {
                                            "bool": {
                                                "must": [
                                                    {
                                                        "term": {
                                                            "writers.uuid": person_id
                                                        }
                                                    }
                                                ]
                                            }
                                        },
                                    }
                                },
                                {
                                    "nested": {
                                        "path": "directors",
                                        "query": {
                                            "bool": {
                                                "must": [
                                                    {
                                                        "term": {
                                                            "directors.uuid": person_id
                                                        }
                                                    }
                                                ]
                                            }
                                        },
                                    }
                                },
                            ]
                        }
                    }
                }
            else:
                body = {"query": {"match_all": {}}}

            if page_size:
                body["size"] = page_size

            if page_number:
                body["from"] = (page_number - 1) * (page_size or 0)

            if sort == "-imdb_rating":
                sort_order = "imdb_rating:desc"
            elif sort == "imdb_rating":
                sort_order = "imdb_rating:asc"
            else:
                sort_order = None

            data = await self.connection.search(
                index=settings.index_movies, body=body, sort=sort_order
            )
            return [Film(**doc["_source"]) for doc in data["hits"]["hits"]]
        except NotFoundError:
            return None

    async def get_list_genres(self, params: dict) -> list[Genre] | None:
        try:
            body = {"query": {"match_all": {}}}
            data = await self.connection.search(
                index=settings.index_genres, body=body, size=9999
            )
            return [Genre(**doc["_source"]) for doc in data["hits"]["hits"]]
        except NotFoundError:
            return None

    async def get_list_persons(self, params: dict) -> list[Person] | None:
        query = params.get("query")
        page_size = params.get("page_size")
        page_number = params.get("page_number")
        try:
            body = {}
            if query:
                body = {"query": {"bool": {"must": {"match": {"full_name": query}}}}}
            if page_size:
                body["size"] = page_size
            if page_number:
                body["from"] = (page_number - 1) * (page_size or 0)
            data = await self.connection.search(index=settings.index_persons, body=body)
            return [Person(**doc["_source"]) for doc in data["hits"]["hits"]]
        except NotFoundError:
            return None
