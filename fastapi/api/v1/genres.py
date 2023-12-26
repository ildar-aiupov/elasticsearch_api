from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, UUID4

from core.config import settings
from services.genre import GenreService, get_genre_service


router = APIRouter()


class ResponseGenre(BaseModel):
    uuid: UUID4
    name: str | None


@router.get(
    "/", response_model=list[ResponseGenre], description="Show list of all genres"
)
async def genrelist(
    genre_service: GenreService = Depends(get_genre_service),
) -> list[ResponseGenre]:
    genrelist = await genre_service.get_list()
    if not genrelist:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=settings.not_found_message
        )
    genrelist = [ResponseGenre(**doc.model_dump()) for doc in genrelist]
    return genrelist


@router.get(
    "/{genre_id}", response_model=ResponseGenre, description="Show one genre by its id"
)
async def genre_details(
    genre_id: str, genre_service: GenreService = Depends(get_genre_service)
) -> ResponseGenre:
    genre = await genre_service.get_entry(genre_id)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=settings.not_found_message
        )
    return ResponseGenre(**genre.model_dump())
