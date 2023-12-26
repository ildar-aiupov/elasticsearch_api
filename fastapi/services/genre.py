from functools import lru_cache
import logging

from fastapi import Depends

from models.genre import Genre
from core.config import settings
from db.storage_interface import StorageInterface
from db.cache_interface import CacheInterface
from db.current_storage import get_current_storage
from db.current_cache import get_current_cache


@lru_cache()
def get_genre_service(
    cache: CacheInterface = Depends(get_current_cache),
    storage: StorageInterface = Depends(get_current_storage),
) -> "GenreService":
    return GenreService(cache, storage)


class GenreService:
    def __init__(self, cache: CacheInterface, storage: StorageInterface):
        self.cache = cache
        self.storage = storage

    async def get_entry(self, genre_id: str) -> Genre | None:
        params = {"index": settings.index_genres, "id": genre_id}
        if genre := await self.cache.get(
            type_data="entry", model_class=Genre, params=params
        ):
            logging.info("Value was taken from cache")
            return genre
        if genre := await self.storage.get_entry(params=params):
            logging.info("Value was taken from storage")
            await self.cache.set(type_data="entry", value=genre, params=params)
            return genre
        return None

    async def get_list(self) -> list[Genre] | None:
        params = {"index": settings.index_genres}
        if genrelist := await self.cache.get(
            type_data="list", model_class=Genre, params=params
        ):
            logging.info("Value was taken from cache")
            return genrelist
        if genrelist := await self.storage.get_list(params=params):
            logging.info("Value was taken from storage")
            await self.cache.set(type_data="list", value=genrelist, params=params)
            return genrelist
        return None
