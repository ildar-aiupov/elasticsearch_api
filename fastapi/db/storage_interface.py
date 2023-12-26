from abc import ABC, abstractmethod

from typing import Any


class StorageInterface(ABC):
    @abstractmethod
    async def get_entry(self, params: dict) -> Any | None:
        ...

    @abstractmethod
    async def get_list(self, params: dict) -> list[Any] | None:
        ...
