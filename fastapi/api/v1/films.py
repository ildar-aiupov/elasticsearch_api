from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, UUID4

from core.config import settings
from services.film import (
    FilmService,
    get_film_service,
)


router = APIRouter()
person_in_films_router = APIRouter()


class ResponseFilm(BaseModel):
    uuid: UUID4
    title: str | None
    imdb_rating: float | None
    description: str | None
    genre: list[dict] | None
    actors: list[dict] | None
    writers: list[dict] | None
    directors: list[dict] | None


class ResponseFilmShort(BaseModel):
    uuid: UUID4
    title: str | None
    imdb_rating: float | None


@person_in_films_router.get(
    "/",
    response_model=list[ResponseFilmShort],
    description="Show list of films by person id",
)
@router.get(
    "/search",
    response_model=list[ResponseFilmShort],
    description="Search films by query",
)
@router.get(
    "/",
    response_model=list[ResponseFilmShort],
    description="Show list of films - just show, sorted or by genre id",
)
async def filmlist(
    page_size: Annotated[
        int, Query(description="Pagination page size", ge=1)
    ] = settings.default_films_pagin_page_size,
    page_number: Annotated[int, Query(description="Pagination page number", ge=1)] = 1,
    person_id: str | None = None,
    query: str | None = None,
    sort: str | None = None,
    genre: str | None = None,
    film_service: FilmService = Depends(get_film_service),
) -> list[ResponseFilmShort]:
    filmlist = await film_service.get_list(
        person_id, query, sort, genre, page_size, page_number
    )
    if not filmlist:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=settings.not_found_message
        )
    filmlist = [ResponseFilmShort(**doc.model_dump()) for doc in filmlist]
    return filmlist


@router.get(
    "/{film_id}", response_model=ResponseFilm, description="Show one film by its id"
)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> ResponseFilm:
    film = await film_service.get_entry(film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=settings.not_found_message
        )
    return ResponseFilm(**film.model_dump())
