from pydantic import UUID4

from models.baseorjsonmodel import BaseOrjsonModel


class Person(BaseOrjsonModel):
    uuid: UUID4
    full_name: str | None
    films: list[dict] | None
