from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, UUID4

from core.config import settings
from services.person import PersonService, get_person_service


router = APIRouter()


class ResponsePerson(BaseModel):
    uuid: UUID4
    full_name: str | None
    films: list[dict] | None


@router.get(
    "/search",
    response_model=list[ResponsePerson],
    description="Search persons by query",
)
async def personlist(
    query: str | None = None,
    page_size: Annotated[
        int, Query(description="Pagination page size", ge=1)
    ] = settings.default_persons_pagin_page_size,
    page_number: Annotated[int, Query(description="Pagination page number", ge=1)] = 1,
    person_service: PersonService = Depends(get_person_service),
) -> list[ResponsePerson]:
    personlist = await person_service.get_list(query, page_size, page_number)
    if not personlist:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=settings.not_found_message
        )
    personlist = [ResponsePerson(**doc.model_dump()) for doc in personlist]
    return personlist


@router.get(
    "/{person_id}",
    response_model=ResponsePerson,
    description="Show one person by his id",
)
async def person_details(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> ResponsePerson:
    person = await person_service.get_entry(person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=settings.not_found_message
        )
    return ResponsePerson(**person.model_dump())
