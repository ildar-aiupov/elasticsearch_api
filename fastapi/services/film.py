from functools import lru_cache
import logging

from fastapi import Depends

from models.film import Film
from core.config import settings
from db.storage_interface import StorageInterface
from db.cache_interface import CacheInterface
from db.current_storage import get_current_storage
from db.current_cache import get_current_cache


@lru_cache()
def get_film_service(
    cache: CacheInterface = Depends(get_current_cache),
    storage: StorageInterface = Depends(get_current_storage),
) -> "FilmService":
    return FilmService(cache, storage)


class FilmService:
    def __init__(self, cache: CacheInterface, storage: StorageInterface):
        self.cache = cache
        self.storage = storage

    async def get_entry(self, film_id: str) -> Film | None:
        params = {"index": settings.index_movies, "id": film_id}
        if film := await self.cache.get(
            type_data="entry", model_class=Film, params=params
        ):
            logging.info("Value was taken from cache")
            return film
        if film := await self.storage.get_entry(params=params):
            logging.info("Value was taken from storage")
            await self.cache.set(type_data="entry", value=film, params=params)
            return film
        return None

    async def get_list(
        self,
        person_id: str,
        query: str,
        sort: str,
        genre: str,
        page_size: int,
        page_number: int,
    ) -> list[Film] | None:
        params = {
            "index": settings.index_movies,
            "person_id": person_id,
            "query": query,
            "sort": sort,
            "genre": genre,
            "page_size": page_size,
            "page_number": page_number,
        }
        if filmlist := await self.cache.get(
            type_data="list", model_class=Film, params=params
        ):
            logging.info("Value was taken from cache")
            return filmlist
        if filmlist := await self.storage.get_list(params=params):
            logging.info("Value was taken from storage")
            await self.cache.set(type_data="list", value=filmlist, params=params)
            return filmlist
        return None
