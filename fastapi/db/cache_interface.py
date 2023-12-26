from abc import ABC, abstractmethod

from typing import Any


class CacheInterface(ABC):
    @abstractmethod
    async def get(self, cache_key) -> Any | None:
        ...

    @abstractmethod
    async def set(self, cache_value) -> None:
        ...
