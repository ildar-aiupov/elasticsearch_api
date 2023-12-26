from pydantic import UUID4

from models.baseorjsonmodel import BaseOrjsonModel


class Film(BaseOrjsonModel):
    uuid: UUID4
    title: str | None
    imdb_rating: float | None
    description: str | None
    genre: list[dict] | None
    actors: list[dict] | None
    writers: list[dict] | None
    directors: list[dict] | None
