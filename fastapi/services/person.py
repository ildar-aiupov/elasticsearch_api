from functools import lru_cache
import logging

from fastapi import Depends

from models.person import Person
from core.config import settings
from db.storage_interface import StorageInterface
from db.cache_interface import CacheInterface
from db.current_storage import get_current_storage
from db.current_cache import get_current_cache


@lru_cache()
def get_person_service(
    cache: CacheInterface = Depends(get_current_cache),
    storage: StorageInterface = Depends(get_current_storage),
) -> "PersonService":
    return PersonService(cache, storage)


class PersonService:
    def __init__(self, cache: CacheInterface, storage: StorageInterface):
        self.cache = cache
        self.storage = storage

    async def get_entry(self, person_id: str) -> Person | None:
        params = {"index": settings.index_persons, "id": person_id}
        if person := await self.cache.get(
            type_data="entry", model_class=Person, params=params
        ):
            logging.info("Value was taken from cache")
            return person
        if person := await self.storage.get_entry(params=params):
            logging.info("Value was taken from storage")
            await self.cache.set(type_data="entry", value=person, params=params)
            return person
        return None

    async def get_list(
        self,
        query: str,
        page_size: int,
        page_number: int,
    ) -> list[Person] | None:
        params = {
            "index": settings.index_persons,
            "query": query,
            "page_size": page_size,
            "page_number": page_number,
        }
        if personlist := await self.cache.get(
            type_data="list", model_class=Person, params=params
        ):
            logging.info("Value was taken from cache")
            return personlist
        if personlist := await self.storage.get_list(params=params):
            logging.info("Value was taken from storage")
            await self.cache.set(type_data="list", value=personlist, params=params)
            return personlist
        return None
