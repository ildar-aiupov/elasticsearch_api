from pydantic import UUID4

from models.baseorjsonmodel import BaseOrjsonModel


class Genre(BaseOrjsonModel):
    uuid: UUID4
    name: str | None
