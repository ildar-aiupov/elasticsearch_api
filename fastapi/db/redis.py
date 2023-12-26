import json
from redis.asyncio import Redis

from core.config import settings
from models.baseorjsonmodel import BaseOrjsonModel
from .cache_interface import CacheInterface


class AsyncRedisCacheEngine(CacheInterface):
    connection: Redis

    def __init__(self):
        self.connection = Redis(host=settings.redis_host, port=settings.redis_port)

    async def close(self) -> None:
        await self.connection.close()

    async def get(
        self, type_data: str, model_class: BaseOrjsonModel, params: dict
    ) -> BaseOrjsonModel | list[BaseOrjsonModel] | None:
        cache_key = "-".join(map(str, params))
        if data := await self.connection.get(cache_key):
            if type_data == "entry":
                return model_class.model_validate_json(data)
            if type_data == "list":
                return [
                    model_class.model_validate_json(doc)
                    for doc in json.loads(data.decode())
                ]
        return None

    async def set(
        self,
        type_data: str,
        value: BaseOrjsonModel | list[BaseOrjsonModel],
        params: dict,
    ) -> None:
        cache_key = "-".join(map(str, params))
        if type_data == "entry":
            value = value.model_dump_json()
        if type_data == "list":
            value = json.dumps([doc.model_dump_json() for doc in value])
        await self.connection.set(cache_key, value, settings.film_cache_time)
